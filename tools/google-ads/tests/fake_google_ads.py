"""Fake Google Ads client for offline unit tests (real v24 proto types, no OAuth)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from google.ads.googleads.v24.common.types.ad_asset import AdTextAsset
from google.ads.googleads.v24.enums.types.ad_group_ad_status import AdGroupAdStatusEnum
from google.ads.googleads.v24.enums.types.ad_group_criterion_status import (
    AdGroupCriterionStatusEnum,
)
from google.ads.googleads.v24.enums.types.ad_group_status import AdGroupStatusEnum
from google.ads.googleads.v24.enums.types.ad_group_type import AdGroupTypeEnum
from google.ads.googleads.v24.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v24.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v24.enums.types.asset_link_status import AssetLinkStatusEnum
from google.ads.googleads.v24.enums.types.budget_delivery_method import (
    BudgetDeliveryMethodEnum,
)
from google.ads.googleads.v24.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v24.enums.types.custom_conversion_goal_status import (
    CustomConversionGoalStatusEnum,
)
from google.ads.googleads.v24.enums.types.eu_political_advertising_status import (
    EuPoliticalAdvertisingStatusEnum,
)
from google.ads.googleads.v24.enums.types.goal_config_level import GoalConfigLevelEnum
from google.ads.googleads.v24.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v24.enums.types.negative_geo_target_type import (
    NegativeGeoTargetTypeEnum,
)
from google.ads.googleads.v24.enums.types.positive_geo_target_type import (
    PositiveGeoTargetTypeEnum,
)
from google.ads.googleads.v24.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v24.services.services.ad_group_service.client import (
    AdGroupServiceClient,
)
from google.ads.googleads.v24.services.services.asset_service.client import (
    AssetServiceClient,
)
from google.ads.googleads.v24.services.services.campaign_budget_service.client import (
    CampaignBudgetServiceClient,
)
from google.ads.googleads.v24.services.services.campaign_service.client import (
    CampaignServiceClient,
)
from google.ads.googleads.v24.services.services.conversion_goal_campaign_config_service.client import (  # noqa: E501
    ConversionGoalCampaignConfigServiceClient,
)
from google.ads.googleads.v24.services.services.custom_conversion_goal_service.client import (
    CustomConversionGoalServiceClient,
)
from google.ads.googleads.v24.services.types.ad_group_ad_service import AdGroupAdOperation
from google.ads.googleads.v24.services.types.ad_group_criterion_service import (
    AdGroupCriterionOperation,
)
from google.ads.googleads.v24.services.types.ad_group_service import AdGroupOperation
from google.ads.googleads.v24.services.types.asset_service import AssetOperation
from google.ads.googleads.v24.services.types.campaign_asset_service import (
    CampaignAssetOperation,
)
from google.ads.googleads.v24.services.types.campaign_budget_service import (
    CampaignBudgetOperation,
)
from google.ads.googleads.v24.services.types.campaign_criterion_service import (
    CampaignCriterionOperation,
)
from google.ads.googleads.v24.services.types.campaign_service import CampaignOperation
from google.ads.googleads.v24.services.types.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigOperation,
)
from google.ads.googleads.v24.services.types.custom_conversion_goal_service import (
    CustomConversionGoalOperation,
)
from google.ads.googleads.v24.services.types.google_ads_service import (
    MutateGoogleAdsRequest,
    MutateOperation,
)

_TYPE_MAP = {
    "MutateOperation": MutateOperation,
    "MutateGoogleAdsRequest": MutateGoogleAdsRequest,
    "CampaignBudgetOperation": CampaignBudgetOperation,
    "CampaignOperation": CampaignOperation,
    "CampaignCriterionOperation": CampaignCriterionOperation,
    "CampaignAssetOperation": CampaignAssetOperation,
    "AssetOperation": AssetOperation,
    "AdGroupOperation": AdGroupOperation,
    "AdGroupCriterionOperation": AdGroupCriterionOperation,
    "AdGroupAdOperation": AdGroupAdOperation,
    "AdTextAsset": AdTextAsset,
    "CustomConversionGoalOperation": CustomConversionGoalOperation,
    "ConversionGoalCampaignConfigOperation": ConversionGoalCampaignConfigOperation,
}

_SERVICE_MAP = {
    "CampaignService": CampaignServiceClient,
    "CampaignBudgetService": CampaignBudgetServiceClient,
    "AdGroupService": AdGroupServiceClient,
    "AssetService": AssetServiceClient,
    "CustomConversionGoalService": CustomConversionGoalServiceClient,
    "ConversionGoalCampaignConfigService": ConversionGoalCampaignConfigServiceClient,
}


class FakeGoogleAdsService:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.validate_only_error: Exception | None = None
        self.execute_error: Exception | None = None
        self.execute_response: Any = SimpleNamespace(mutate_operation_responses=[])

    def mutate(self, request: Any = None, **kwargs: Any) -> Any:
        if request is not None:
            payload = {
                "customer_id": request.customer_id,
                "mutate_operations": list(request.mutate_operations),
                "partial_failure": bool(request.partial_failure),
                "validate_only": bool(request.validate_only),
                "response_content_type": request.response_content_type,
                "request": request,
            }
        else:
            payload = kwargs
        self.calls.append(payload)
        if payload.get("validate_only"):
            if self.validate_only_error:
                raise self.validate_only_error
            return SimpleNamespace(mutate_operation_responses=[])
        if self.execute_error:
            raise self.execute_error
        return self.execute_response


class FakeGoogleAdsClient:
    """Minimal client surface used by builders/create (no network)."""

    def __init__(self) -> None:
        self.enums = SimpleNamespace(
            CampaignStatusEnum=CampaignStatusEnum.CampaignStatus,
            AdGroupStatusEnum=AdGroupStatusEnum.AdGroupStatus,
            AdGroupAdStatusEnum=AdGroupAdStatusEnum.AdGroupAdStatus,
            AdGroupCriterionStatusEnum=AdGroupCriterionStatusEnum.AdGroupCriterionStatus,
            AdGroupTypeEnum=AdGroupTypeEnum.AdGroupType,
            AdvertisingChannelTypeEnum=AdvertisingChannelTypeEnum.AdvertisingChannelType,
            AssetFieldTypeEnum=AssetFieldTypeEnum.AssetFieldType,
            AssetLinkStatusEnum=AssetLinkStatusEnum.AssetLinkStatus,
            BudgetDeliveryMethodEnum=BudgetDeliveryMethodEnum.BudgetDeliveryMethod,
            KeywordMatchTypeEnum=KeywordMatchTypeEnum.KeywordMatchType,
            PositiveGeoTargetTypeEnum=PositiveGeoTargetTypeEnum.PositiveGeoTargetType,
            NegativeGeoTargetTypeEnum=NegativeGeoTargetTypeEnum.NegativeGeoTargetType,
            ResponseContentTypeEnum=ResponseContentTypeEnum.ResponseContentType,
            EuPoliticalAdvertisingStatusEnum=(
                EuPoliticalAdvertisingStatusEnum.EuPoliticalAdvertisingStatus
            ),
            CustomConversionGoalStatusEnum=(
                CustomConversionGoalStatusEnum.CustomConversionGoalStatus
            ),
            GoalConfigLevelEnum=GoalConfigLevelEnum.GoalConfigLevel,
        )
        self.google_ads_service = FakeGoogleAdsService()

    def get_type(self, name: str) -> Any:
        return _TYPE_MAP[name]()

    def get_service(self, name: str) -> Any:
        if name == "GoogleAdsService":
            return self.google_ads_service
        return _SERVICE_MAP[name]
