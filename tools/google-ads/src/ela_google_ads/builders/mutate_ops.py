"""Build Google Ads API mutate operations for PAUSED Search campaign create.

Uses the installed google-ads client library (default API v24). Budgets have no
PAUSED status in BudgetStatusEnum — only ENABLED/REMOVED — so budgets are created
ENABLED (they do not spend while the campaign remains PAUSED).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ela_google_ads.builders.tracking import build_final_url_suffix
from ela_google_ads.exceptions import MutationSafetyError
from ela_google_ads.models.spec import CampaignSpec, KeywordSpec
from ela_google_ads.safety import assert_new_campaign_paused, assert_status_not_enabled

# Locked campaign-settings ceiling for Maximize Clicks (TargetSpend).
DEFAULT_CPC_BID_CEILING_MICROS = 25_000_000
ELA_CUSTOM_CONVERSION_GOAL_NAME = "ELA | Goals | Nonbrand Search"
ELA_CALL_PHONE_NUMBER = "+14246781416"


def budget_name_for_campaign(campaign_name: str) -> str:
    """Deterministic budget name derived from the ELA Search campaign name."""
    if " | Search | " not in campaign_name:
        raise MutationSafetyError(
            f"Cannot derive budget name from non-ELA Search campaign: {campaign_name!r}"
        )
    return campaign_name.replace(" | Search | ", " | Budget | ", 1)


def currency_to_micros(amount: float) -> int:
    return int(round(float(amount) * 1_000_000))


@dataclass
class TempIdAllocator:
    """Allocate negative temporary resource IDs for atomic GoogleAdsService.mutate."""

    _next: int = -1

    def next_id(self) -> str:
        value = str(self._next)
        self._next -= 1
        return value


@dataclass
class BuiltMutatePlan:
    """Operations plus a human-readable inventory of intended creates."""

    operations: list[Any]
    planned_resources: list[dict[str, Any]] = field(default_factory=list)
    budget_resource_name: str | None = None
    campaign_resource_name: str | None = None
    budget_reused: bool = False
    notes: list[str] = field(default_factory=list)


def build_campaign_create_operations(
    client: Any,
    *,
    customer_id: str,
    spec: CampaignSpec,
    existing_budget_resource_name: str | None = None,
    existing_custom_goal_resource_name: str | None = None,
    cpc_bid_ceiling_micros: int = DEFAULT_CPC_BID_CEILING_MICROS,
) -> BuiltMutatePlan:
    """Build atomic mutate operations for a new PAUSED ELA Nonbrand Search campaign."""
    assert_new_campaign_paused(spec.status)
    assert_status_not_enabled(spec.status, resource="campaign")

    if not spec.geo_target_ids:
        raise MutationSafetyError(
            "geo_target_ids are required for API create (names alone are not enough)."
        )

    alloc = TempIdAllocator()
    operations: list[Any] = []
    planned: list[dict[str, Any]] = []
    notes: list[str] = [
        "Campaign/ad groups/keywords/AdGroupAds/asset links created PAUSED.",
        "Campaign budgets have no PAUSED API status; the budget is inert under a PAUSED campaign.",
        "Location/language criteria are ready but cannot serve while the campaign is PAUSED.",
        "Locked shared-list exports are flattened into campaign-level negative criteria.",
    ]

    campaign_service = client.get_service("CampaignService")
    budget_service = client.get_service("CampaignBudgetService")
    ad_group_service = client.get_service("AdGroupService")
    asset_service = client.get_service("AssetService")
    custom_goal_service = client.get_service("CustomConversionGoalService")
    goal_config_service = client.get_service("ConversionGoalCampaignConfigService")

    # --- Shared ELA custom conversion goal (create once, then reuse by exact name) ---
    if existing_custom_goal_resource_name:
        custom_goal_resource = existing_custom_goal_resource_name
        planned.append(
            {
                "action": "reuse",
                "type": "custom_conversion_goal",
                "name": ELA_CUSTOM_CONVERSION_GOAL_NAME,
                "resource_name": custom_goal_resource,
                "status": "ENABLED",
            }
        )
    else:
        if not spec.conversion_goals:
            raise MutationSafetyError(
                "At least one locked conversion action ID is required."
            )
        custom_goal_temp = alloc.next_id()
        custom_goal_resource = custom_goal_service.custom_conversion_goal_path(
            customer_id, custom_goal_temp
        )
        custom_goal_op = client.get_type("CustomConversionGoalOperation")
        custom_goal = custom_goal_op.create
        custom_goal.resource_name = custom_goal_resource
        custom_goal.name = ELA_CUSTOM_CONVERSION_GOAL_NAME
        custom_goal.status = client.enums.CustomConversionGoalStatusEnum.ENABLED
        for conversion_action_id in spec.conversion_goals:
            custom_goal.conversion_actions.append(
                f"customers/{customer_id}/conversionActions/{conversion_action_id}"
            )
        operations.append(
            _mutate_op(client, custom_conversion_goal_operation=custom_goal_op)
        )
        planned.append(
            {
                "action": "create",
                "type": "custom_conversion_goal",
                "name": ELA_CUSTOM_CONVERSION_GOAL_NAME,
                "resource_name": custom_goal_resource,
                "conversion_action_ids": list(spec.conversion_goals),
                "status": "ENABLED",
            }
        )

    # --- Budget ---
    budget_name = budget_name_for_campaign(spec.name)
    if existing_budget_resource_name:
        budget_resource = existing_budget_resource_name
        budget_reused = True
        planned.append(
            {
                "action": "reuse",
                "type": "campaign_budget",
                "name": budget_name,
                "resource_name": budget_resource,
                "status": "ENABLED",
            }
        )
    else:
        budget_temp = alloc.next_id()
        budget_resource = budget_service.campaign_budget_path(customer_id, budget_temp)
        budget_op = client.get_type("CampaignBudgetOperation")
        budget = budget_op.create
        budget.resource_name = budget_resource
        budget.name = budget_name
        budget.amount_micros = currency_to_micros(spec.daily_budget)
        budget.explicitly_shared = False
        budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        # BudgetStatusEnum has no PAUSED — omit status (API defaults to ENABLED).
        operations.append(_mutate_op(client, campaign_budget_operation=budget_op))
        budget_reused = False
        planned.append(
            {
                "action": "create",
                "type": "campaign_budget",
                "name": budget_name,
                "resource_name": budget_resource,
                "status": "ENABLED",
                "note": "API BudgetStatusEnum has no PAUSED",
            }
        )

    # --- Campaign ---
    campaign_temp = alloc.next_id()
    campaign_resource = campaign_service.campaign_path(customer_id, campaign_temp)
    campaign_op = client.get_type("CampaignOperation")
    campaign = campaign_op.create
    campaign.resource_name = campaign_resource
    campaign.name = spec.name
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    campaign.campaign_budget = budget_resource
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = False
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False
    campaign.geo_target_type_setting.positive_geo_target_type = (
        client.enums.PositiveGeoTargetTypeEnum.PRESENCE
    )
    campaign.geo_target_type_setting.negative_geo_target_type = (
        client.enums.NegativeGeoTargetTypeEnum.PRESENCE
    )
    # Maximize Clicks == TargetSpend in the Google Ads API.
    campaign.target_spend.cpc_bid_ceiling_micros = cpc_bid_ceiling_micros
    if spec.tracking.final_url_suffix:
        # Campaign-level suffix uses campaign slug; per-ad-group set on ads.
        campaign.final_url_suffix = build_final_url_suffix(
            campaign_name=spec.name,
            ad_group_name="",
            custom_suffix=spec.tracking.final_url_suffix,
        )
    if spec.tracking.tracking_template:
        campaign.tracking_url_template = spec.tracking.tracking_template
    operations.append(_mutate_op(client, campaign_operation=campaign_op))
    planned.append(
        {
            "action": "create",
            "type": "campaign",
            "name": spec.name,
            "resource_name": campaign_resource,
            "status": "PAUSED",
        }
    )

    # Give the new campaign its own goal configuration pointing at the locked
    # ELA custom conversion goal. This changes only the campaign created above.
    goal_config_op = client.get_type("ConversionGoalCampaignConfigOperation")
    goal_config = goal_config_op.update
    goal_config.resource_name = goal_config_service.conversion_goal_campaign_config_path(
        customer_id, campaign_temp
    )
    goal_config.campaign = campaign_resource
    goal_config.goal_config_level = client.enums.GoalConfigLevelEnum.CAMPAIGN
    goal_config.custom_conversion_goal = custom_goal_resource
    goal_config_op.update_mask.paths.extend(
        ["goal_config_level", "custom_conversion_goal"]
    )
    operations.append(
        _mutate_op(
            client,
            conversion_goal_campaign_config_operation=goal_config_op,
        )
    )
    planned.append(
        {
            "action": "create",
            "type": "conversion_goal_campaign_config",
            "campaign": campaign_resource,
            "custom_conversion_goal": custom_goal_resource,
            "conversion_action_ids": list(spec.conversion_goals),
            "status": "CAMPAIGN_SPECIFIC",
        }
    )

    # --- Geo + language criteria ---
    for geo_id in spec.geo_target_ids:
        crit_op = client.get_type("CampaignCriterionOperation")
        criterion = crit_op.create
        criterion.campaign = campaign_resource
        criterion.location.geo_target_constant = f"geoTargetConstants/{geo_id}"
        operations.append(_mutate_op(client, campaign_criterion_operation=crit_op))
        planned.append(
            {
                "action": "create",
                "type": "campaign_criterion.location",
                "geo_target_id": geo_id,
                "campaign": campaign_resource,
                "status": "ENABLED",
            }
        )

    for lang_id in spec.language_ids:
        crit_op = client.get_type("CampaignCriterionOperation")
        criterion = crit_op.create
        criterion.campaign = campaign_resource
        criterion.language.language_constant = f"languageConstants/{lang_id}"
        operations.append(_mutate_op(client, campaign_criterion_operation=crit_op))
        planned.append(
            {
                "action": "create",
                "type": "campaign_criterion.language",
                "language_id": lang_id,
                "campaign": campaign_resource,
                "status": "ENABLED",
            }
        )

    # --- Campaign negative keywords ---
    for kw in spec.campaign_negative_keywords:
        operations.append(
            _keyword_criterion_op(
                client,
                campaign_resource=campaign_resource,
                keyword=kw,
                negative=True,
                level="campaign",
            )
        )
        planned.append(
            {
                "action": "create",
                "type": "campaign_criterion.negative_keyword",
                "text": kw.text,
                "match_type": kw.match_type.upper(),
                "status": "ENABLED",
            }
        )

    # --- Assets + PAUSED campaign asset links ---
    for sitelink in spec.sitelinks:
        asset_temp = alloc.next_id()
        asset_resource = asset_service.asset_path(customer_id, asset_temp)
        asset_op = client.get_type("AssetOperation")
        asset = asset_op.create
        asset.resource_name = asset_resource
        asset.name = f"{spec.name} | Sitelink | {sitelink.get('link_text', '')}"
        asset.final_urls.append(str(sitelink.get("final_url") or spec.final_url))
        asset.sitelink_asset.link_text = str(sitelink.get("link_text") or "")[:25]
        if sitelink.get("description1"):
            asset.sitelink_asset.description1 = str(sitelink["description1"])[:35]
        if sitelink.get("description2"):
            asset.sitelink_asset.description2 = str(sitelink["description2"])[:35]
        operations.append(_mutate_op(client, asset_operation=asset_op))
        link_op = client.get_type("CampaignAssetOperation")
        link = link_op.create
        link.campaign = campaign_resource
        link.asset = asset_resource
        link.field_type = client.enums.AssetFieldTypeEnum.SITELINK
        link.status = client.enums.AssetLinkStatusEnum.PAUSED
        operations.append(_mutate_op(client, campaign_asset_operation=link_op))
        planned.append(
            {
                "action": "create",
                "type": "campaign_asset.sitelink",
                "name": asset.name,
                "asset_resource_name": asset_resource,
                "status": "PAUSED",
            }
        )

    for callout_text in spec.callouts:
        asset_temp = alloc.next_id()
        asset_resource = asset_service.asset_path(customer_id, asset_temp)
        asset_op = client.get_type("AssetOperation")
        asset = asset_op.create
        asset.resource_name = asset_resource
        asset.name = f"{spec.name} | Callout | {callout_text}"
        asset.callout_asset.callout_text = str(callout_text)[:25]
        operations.append(_mutate_op(client, asset_operation=asset_op))
        link_op = client.get_type("CampaignAssetOperation")
        link = link_op.create
        link.campaign = campaign_resource
        link.asset = asset_resource
        link.field_type = client.enums.AssetFieldTypeEnum.CALLOUT
        link.status = client.enums.AssetLinkStatusEnum.PAUSED
        operations.append(_mutate_op(client, campaign_asset_operation=link_op))
        planned.append(
            {
                "action": "create",
                "type": "campaign_asset.callout",
                "name": asset.name,
                "asset_resource_name": asset_resource,
                "status": "PAUSED",
            }
        )

    for snippet in spec.structured_snippets:
        asset_temp = alloc.next_id()
        asset_resource = asset_service.asset_path(customer_id, asset_temp)
        asset_op = client.get_type("AssetOperation")
        asset = asset_op.create
        asset.resource_name = asset_resource
        header = str(snippet.get("header") or "")
        asset.name = f"{spec.name} | Snippet | {header}"
        asset.structured_snippet_asset.header = header
        for value in snippet.get("values") or []:
            asset.structured_snippet_asset.values.append(str(value))
        operations.append(_mutate_op(client, asset_operation=asset_op))
        link_op = client.get_type("CampaignAssetOperation")
        link = link_op.create
        link.campaign = campaign_resource
        link.asset = asset_resource
        link.field_type = client.enums.AssetFieldTypeEnum.STRUCTURED_SNIPPET
        link.status = client.enums.AssetLinkStatusEnum.PAUSED
        operations.append(_mutate_op(client, campaign_asset_operation=link_op))
        planned.append(
            {
                "action": "create",
                "type": "campaign_asset.structured_snippet",
                "name": asset.name,
                "asset_resource_name": asset_resource,
                "status": "PAUSED",
            }
        )

    # Approved HubSpot number. The asset has no serving status; its campaign
    # link is PAUSED, matching every other newly attached campaign asset.
    call_asset_temp = alloc.next_id()
    call_asset_resource = asset_service.asset_path(customer_id, call_asset_temp)
    call_asset_op = client.get_type("AssetOperation")
    call_asset = call_asset_op.create
    call_asset.resource_name = call_asset_resource
    call_asset.name = f"{spec.name} | Call | 424-678-1416"
    call_asset.call_asset.country_code = "US"
    call_asset.call_asset.phone_number = ELA_CALL_PHONE_NUMBER
    operations.append(_mutate_op(client, asset_operation=call_asset_op))
    call_link_op = client.get_type("CampaignAssetOperation")
    call_link = call_link_op.create
    call_link.campaign = campaign_resource
    call_link.asset = call_asset_resource
    call_link.field_type = client.enums.AssetFieldTypeEnum.CALL
    call_link.status = client.enums.AssetLinkStatusEnum.PAUSED
    operations.append(_mutate_op(client, campaign_asset_operation=call_link_op))
    planned.append(
        {
            "action": "create",
            "type": "campaign_asset.call",
            "name": call_asset.name,
            "asset_resource_name": call_asset_resource,
            "phone_number": ELA_CALL_PHONE_NUMBER,
            "status": "PAUSED",
        }
    )

    # --- Ad groups / keywords / RSAs ---
    for ag in spec.ad_groups:
        ag_temp = alloc.next_id()
        ag_resource = ad_group_service.ad_group_path(customer_id, ag_temp)
        ag_op = client.get_type("AdGroupOperation")
        ad_group = ag_op.create
        ad_group.resource_name = ag_resource
        ad_group.name = ag.name
        ad_group.campaign = campaign_resource
        ad_group.status = client.enums.AdGroupStatusEnum.PAUSED
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        operations.append(_mutate_op(client, ad_group_operation=ag_op))
        planned.append(
            {
                "action": "create",
                "type": "ad_group",
                "name": ag.name,
                "resource_name": ag_resource,
                "status": "PAUSED",
            }
        )

        for kw in ag.keywords:
            assert_status_not_enabled("PAUSED", resource=f"keyword:{kw.text}")
            crit_op = client.get_type("AdGroupCriterionOperation")
            criterion = crit_op.create
            criterion.ad_group = ag_resource
            criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
            criterion.keyword.text = kw.text
            criterion.keyword.match_type = _match_type_enum(client, kw.match_type)
            operations.append(_mutate_op(client, ad_group_criterion_operation=crit_op))
            planned.append(
                {
                    "action": "create",
                    "type": "ad_group_criterion.keyword",
                    "ad_group": ag.name,
                    "text": kw.text,
                    "match_type": kw.match_type.upper(),
                    "status": "PAUSED",
                }
            )

        for kw in ag.negative_keywords:
            crit_op = client.get_type("AdGroupCriterionOperation")
            criterion = crit_op.create
            criterion.ad_group = ag_resource
            criterion.negative = True
            criterion.keyword.text = kw.text
            criterion.keyword.match_type = _match_type_enum(client, kw.match_type)
            operations.append(_mutate_op(client, ad_group_criterion_operation=crit_op))
            planned.append(
                {
                    "action": "create",
                    "type": "ad_group_criterion.negative_keyword",
                    "ad_group": ag.name,
                    "text": kw.text,
                    "match_type": kw.match_type.upper(),
                    "status": "ENABLED",
                }
            )

        if ag.rsa is None:
            raise MutationSafetyError(f"Ad group {ag.name!r} missing RSA for create")

        final_url = ag.final_url or spec.final_url
        if not final_url:
            raise MutationSafetyError(f"Ad group {ag.name!r} missing final_url")

        ad_op = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_op.create
        ad_group_ad.ad_group = ag_resource
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad = ad_group_ad.ad
        ad.final_urls.append(final_url)
        ad.final_url_suffix = build_final_url_suffix(
            campaign_name=spec.name,
            ad_group_name=ag.name,
            custom_suffix=spec.tracking.final_url_suffix,
        )
        for headline in ag.rsa.headlines:
            asset = client.get_type("AdTextAsset")
            asset.text = headline
            ad.responsive_search_ad.headlines.append(asset)
        for description in ag.rsa.descriptions:
            asset = client.get_type("AdTextAsset")
            asset.text = description
            ad.responsive_search_ad.descriptions.append(asset)
        if ag.rsa.path1:
            ad.responsive_search_ad.path1 = ag.rsa.path1
        if ag.rsa.path2:
            ad.responsive_search_ad.path2 = ag.rsa.path2
        operations.append(_mutate_op(client, ad_group_ad_operation=ad_op))
        planned.append(
            {
                "action": "create",
                "type": "ad_group_ad.rsa",
                "ad_group": ag.name,
                "final_url": final_url,
                "status": "PAUSED",
            }
        )

    return BuiltMutatePlan(
        operations=operations,
        planned_resources=planned,
        budget_resource_name=budget_resource,
        campaign_resource_name=campaign_resource,
        budget_reused=budget_reused,
        notes=notes,
    )


def _mutate_op(client: Any, **kwargs: Any) -> Any:
    op = client.get_type("MutateOperation")
    for key, value in kwargs.items():
        setattr(op, key, value)
    return op


def _match_type_enum(client: Any, match_type: str) -> Any:
    mt = match_type.upper()
    if mt == "EXACT":
        return client.enums.KeywordMatchTypeEnum.EXACT
    if mt == "PHRASE":
        return client.enums.KeywordMatchTypeEnum.PHRASE
    raise MutationSafetyError(f"Unsupported match type for create: {match_type!r}")


def _keyword_criterion_op(
    client: Any,
    *,
    campaign_resource: str,
    keyword: KeywordSpec,
    negative: bool,
    level: str,
) -> Any:
    del level  # documented in planned resources
    crit_op = client.get_type("CampaignCriterionOperation")
    criterion = crit_op.create
    criterion.campaign = campaign_resource
    criterion.negative = negative
    criterion.keyword.text = keyword.text
    criterion.keyword.match_type = _match_type_enum(client, keyword.match_type)
    return _mutate_op(client, campaign_criterion_operation=crit_op)
