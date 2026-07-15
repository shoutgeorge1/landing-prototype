"""Click CLI: audit / export / validate / preview / execute separation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ela_google_ads import __version__
from ela_google_ads.config import load_settings
from ela_google_ads.exceptions import ElaGoogleAdsError, ValidationError
from ela_google_ads.export_utils import export_records, write_json
from ela_google_ads.logging_config import configure_logging, get_logger

console = Console()
logger = get_logger(__name__)


def _print_error(exc: BaseException) -> None:
    console.print(f"[red]Error:[/red] {exc}")
    if isinstance(exc, ValidationError) and exc.issues:
        for issue in exc.issues:
            console.print(f"  - {issue}")


@click.group()
@click.option("--log-level", default="INFO", show_default=True)
@click.version_option(__version__, prog_name="ela-google-ads")
@click.pass_context
def main(ctx: click.Context, log_level: str) -> None:
    """ELA Google Ads automation toolkit (read + guarded PAUSED create)."""
    configure_logging(log_level)
    ctx.ensure_object(dict)
    ctx.obj["settings"] = load_settings()


@main.group()
def account() -> None:
    """Account access and audit commands."""


@account.command("test")
@click.pass_context
def account_test(ctx: click.Context) -> None:
    """Test access to the configured Google Ads customer."""
    from ela_google_ads.account.access import get_account_access_summary

    settings = ctx.obj["settings"]
    try:
        summary = get_account_access_summary(settings)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc

    table = Table(title="Account access")
    table.add_column("Field")
    table.add_column("Value")
    for key, value in summary.items():
        table.add_row(key, str(value))
    console.print(table)


@account.command("list-accessible")
@click.pass_context
def account_list_accessible(ctx: click.Context) -> None:
    """List customer IDs accessible to the OAuth user."""
    from ela_google_ads.account.access import list_accessible_customers

    settings = ctx.obj["settings"]
    try:
        names = list_accessible_customers(settings)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    for name in names:
        console.print(name)


@account.command("audit")
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def account_audit(ctx: click.Context, out_dir: Path | None) -> None:
    """Full read-only account snapshot."""
    from ela_google_ads.account.snapshot import build_account_snapshot

    settings = ctx.obj["settings"]
    try:
        snapshot = build_account_snapshot(settings)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc

    destination = out_dir or settings.output_dir
    paths = export_records(
        destination,
        "account_snapshot",
        [snapshot["account"]],
        metadata={"counts": snapshot["counts"], "warnings": snapshot["warnings"]},
    )
    full_path = write_json(
        destination / f"account_snapshot_full_{paths['json'].stem.split('_')[-1]}.json",
        snapshot,
    )
    console.print(f"Wrote {paths['json']}")
    console.print(f"Wrote {paths['csv']}")
    console.print(f"Wrote {full_path}")
    for warning in snapshot.get("warnings") or []:
        console.print(f"[yellow]Warning:[/yellow] {warning}")


@main.group()
def campaigns() -> None:
    """Campaign export / preview / validate / create (PAUSED; --execute required)."""


@campaigns.command("export")
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def campaigns_export(ctx: click.Context, out_dir: Path | None) -> None:
    from ela_google_ads.campaigns.inventory import list_campaigns

    settings = ctx.obj["settings"]
    try:
        rows = list_campaigns(settings)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    destination = out_dir or settings.output_dir
    paths = export_records(
        destination, "campaigns", rows, metadata={"customer_id": settings.customer_id}
    )
    console.print(f"Exported {len(rows)} campaigns -> {paths['csv']}")


@campaigns.command("validate")
@click.argument("spec_path", type=click.Path(exists=True, path_type=Path))
def campaigns_validate(spec_path: Path) -> None:
    from ela_google_ads.validators.spec_validators import validate_spec_file

    try:
        spec, issues = validate_spec_file(spec_path)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    if issues:
        console.print(f"[red]INVALID[/red] {spec.name}: {len(issues)} issue(s)")
        for issue in issues:
            console.print(f"  - {issue}")
        raise SystemExit(2)
    console.print(f"[green]VALID[/green] {spec.name}")


@campaigns.command("preview")
@click.argument("spec_path", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def campaigns_preview(ctx: click.Context, spec_path: Path, out_dir: Path | None) -> None:
    from ela_google_ads.builders.campaign import build_campaign_preview
    from ela_google_ads.validators.spec_validators import load_spec_file

    settings = ctx.obj["settings"]
    try:
        spec = load_spec_file(spec_path)
        preview = build_campaign_preview(spec)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    destination = out_dir or settings.output_dir
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in spec.name)
    path = write_json(destination / f"preview_{safe_name}.json", preview)
    console.print_json(json.dumps(preview, default=str))
    console.print(f"Wrote {path}")
    if preview["validation_issues"]:
        raise SystemExit(2)


@campaigns.command("create")
@click.argument("spec_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--execute",
    "execute",
    is_flag=True,
    default=False,
    help="Required for live mutation (default is dry-run validate_only)",
)
@click.option(
    "--confirm-customer-id",
    default=None,
    help="Required with --execute; must be 6769947952",
)
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def campaigns_create(
    ctx: click.Context,
    spec_path: Path,
    execute: bool,
    confirm_customer_id: str | None,
    out_dir: Path | None,
) -> None:
    """Create PAUSED ELA Nonbrand Search campaign from spec (dry-run by default)."""
    from ela_google_ads.campaigns.create import create_campaign_from_spec

    settings = ctx.obj["settings"]
    try:
        result = create_campaign_from_spec(
            settings,
            spec_path,
            execute=execute,
            confirm_customer_id_value=confirm_customer_id,
            out_dir=out_dir,
        )
        console.print_json(json.dumps(result, default=str))
        if result.get("log_path"):
            console.print(f"Wrote {result['log_path']}")
        if result.get("skipped"):
            console.print("[yellow]Skipped existing campaign (no mutate).[/yellow]")
        elif execute and result.get("mutated"):
            console.print("[green]Created PAUSED resources.[/green]")
        else:
            console.print("[cyan]Dry-run validate_only complete (no resources created).[/cyan]")
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc


@campaigns.command("create-batch")
@click.argument("spec_paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("--execute", "execute", is_flag=True, default=False)
@click.option("--confirm-customer-id", default=None)
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def campaigns_create_batch(
    ctx: click.Context,
    spec_paths: tuple[Path, ...],
    execute: bool,
    confirm_customer_id: str | None,
    out_dir: Path | None,
) -> None:
    """Dry-run or create multiple PAUSED ELA Nonbrand Search specs."""
    from ela_google_ads.campaigns.create import create_campaigns_from_specs

    if not spec_paths:
        console.print("[red]Provide one or more spec paths.[/red]")
        raise SystemExit(2)

    settings = ctx.obj["settings"]
    try:
        summary = create_campaigns_from_specs(
            settings,
            list(spec_paths),
            execute=execute,
            confirm_customer_id_value=confirm_customer_id,
            out_dir=out_dir,
        )
        console.print_json(json.dumps(summary, default=str))
        if summary.get("log_path"):
            console.print(f"Wrote {summary['log_path']}")
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc


@main.group()
def conversions() -> None:
    """Conversion-action export and mapping."""


@conversions.command("export")
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def conversions_export(ctx: click.Context, out_dir: Path | None) -> None:
    from ela_google_ads.conversions.inventory import list_conversion_actions

    settings = ctx.obj["settings"]
    try:
        rows = list_conversion_actions(settings)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    destination = out_dir or settings.output_dir
    paths = export_records(
        destination,
        "conversion_actions",
        rows,
        metadata={"customer_id": settings.customer_id},
    )
    console.print(f"Exported {len(rows)} conversion actions -> {paths['csv']}")


@main.group()
def assets() -> None:
    """Asset inventory exports."""


@assets.command("export")
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def assets_export(ctx: click.Context, out_dir: Path | None) -> None:
    from ela_google_ads.assets.inventory import list_assets, phone_tracking_warnings

    settings = ctx.obj["settings"]
    try:
        rows = list_assets(settings)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    destination = out_dir or settings.output_dir
    paths = export_records(
        destination, "assets", rows, metadata={"customer_id": settings.customer_id}
    )
    call_assets = [r for r in rows if "CALL" in str(r.get("type", ""))]
    for warning in phone_tracking_warnings(settings, call_assets=call_assets):
        console.print(f"[yellow]Warning:[/yellow] {warning}")
    console.print(f"Exported {len(rows)} assets -> {paths['csv']}")


@main.group()
def reports() -> None:
    """Reporting exports."""


@reports.command("search-terms")
@click.option("--days", default=30, show_default=True, type=click.Choice(["7", "14", "30"]))
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def reports_search_terms(ctx: click.Context, days: str, out_dir: Path | None) -> None:
    from ela_google_ads.reports.search_terms import list_search_terms

    settings = ctx.obj["settings"]
    try:
        rows = list_search_terms(settings, days=int(days))
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    destination = out_dir or settings.output_dir
    paths = export_records(
        destination,
        "search_terms",
        rows,
        metadata={"customer_id": settings.customer_id, "days": int(days)},
    )
    console.print(f"Exported {len(rows)} search terms -> {paths['csv']}")


@main.group()
def specs() -> None:
    """Campaign specification tools."""


@specs.command("validate")
@click.argument("spec_path", type=click.Path(exists=True, path_type=Path))
def specs_validate(spec_path: Path) -> None:
    from ela_google_ads.validators.spec_validators import validate_spec_file

    try:
        spec, issues = validate_spec_file(spec_path)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    if issues:
        console.print(f"[red]INVALID[/red] {spec.name}")
        for issue in issues:
            console.print(f"  - {issue}")
        raise SystemExit(2)
    console.print(f"[green]VALID[/green] {spec.name}")


@main.group()
def geo() -> None:
    """Geo-target lookup utilities."""


@geo.command("search")
@click.argument("query_text")
@click.option("--country", default="US", show_default=True)
@click.pass_context
def geo_search(ctx: click.Context, query_text: str, country: str) -> None:
    from ela_google_ads.builders.geo import search_geo_targets

    settings = ctx.obj["settings"]
    try:
        rows = search_geo_targets(settings, query_text, country_code=country)
    except ElaGoogleAdsError as exc:
        _print_error(exc)
        raise SystemExit(1) from exc
    console.print_json(json.dumps(rows, default=str))


def run() -> int:
    try:
        main(standalone_mode=True)
        return 0
    except SystemExit as exc:
        return int(exc.code or 0)


if __name__ == "__main__":
    sys.exit(main())
