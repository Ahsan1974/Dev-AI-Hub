"""Append enough unique tools to push the catalogue past 1000."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from expand_catalogue_batch2 import make_tool

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "app" / "seed" / "data" / "tools"
DATA = ROOT / "app" / "seed" / "data"

STATUS_MAP = {
    "FT": "FREE_TIER",
    "FF": "FREE_FOREVER",
    "OS": "OPEN_SOURCE",
    "TR": "FREE_TRIAL",
    "CR": "FREE_CREDITS",
    "BK": "BYOK",
    "PD": "PAID_ONLY",
}

EXTRA = r"""
SwaggerHub|https://swagger.io/tools/swaggerhub/|api-development,documentation|TR|0|0|API design and documentation platform
Stoplight Studio|https://stoplight.io|api-development,documentation|FT|0|0|Visual OpenAPI design
Firecamp|https://firecamp.io|api-development|OS|1|0|Open source API platform
Restfox|https://restfox.dev|api-development|OS|1|0|Offline-first web API client
Yaak|https://yaak.app|api-development|OS|1|0|Desktop API client
Kreya|https://kreya.app|api-development|FT|0|0|gRPC and REST GUI client
BloomRPC|https://github.com/bloomrpc/bloomrpc|api-development|OS|1|0|GUI client for gRPC
grpcui|https://github.com/fullstorydev/grpcui|api-development,terminal-cli|OS|1|0|Web UI for gRPC services
grpcurl|https://github.com/fullstorydev/grpcurl|api-development,terminal-cli|OS|1|0|curl for gRPC
Evans gRPC|https://github.com/ktr0731/evans|api-development,terminal-cli|OS|1|0|Interactive gRPC client
Proxyman|https://proxyman.com|browser-devtools,api-development|TR|0|0|Modern HTTP debugging proxy
Charles Proxy|https://www.charlesproxy.com|browser-devtools,api-development|TR|0|0|HTTP proxy and monitor
mitmproxy|https://mitmproxy.org|browser-devtools,api-development,security|OS|1|0|Interactive HTTPS proxy
Fiddler Classic|https://www.telerik.com/fiddler|browser-devtools,api-development|FT|0|0|Web debugging proxy
Whistle Proxy|https://wproxy.org|browser-devtools|OS|1|0|Cross-platform web debugging proxy
Mockoon|https://mockoon.com|api-development,testing|OS|1|0|Local API mocking
WireMock|https://wiremock.org|api-development,testing|OS|1|0|API mock server
Mock Service Worker|https://mswjs.io|api-development,testing|OS|1|0|API mocking for browsers and Node
JSON Server|https://github.com/typicode/json-server|api-development,testing|OS|1|0|Fake REST API from JSON
Prism Mock Server|https://stoplight.io/open-source/prism|api-development,testing|OS|1|0|OpenAPI-driven mock server
Speakeasy|https://www.speakeasy.com|api-development|FT|0|0|API SDK generation
Fern API|https://buildwithfern.com|api-development,documentation|FT|0|0|Generate SDKs and docs from API defs
Stainless SDK|https://www.stainless.com|api-development|TR|0|0|SDK generation from OpenAPI
liblab|https://liblab.com|api-development|TR|0|0|Generate SDKs from APIs
OpenAPI Generator|https://openapi-generator.tech|api-development|OS|1|0|Generate clients from OpenAPI
Swagger Codegen|https://swagger.io/tools/swagger-codegen/|api-development|OS|1|0|Generate API clients and servers
Orval|https://orval.dev|api-development|OS|1|0|Generate TypeScript clients from OpenAPI
Kiota|https://learn.microsoft.com/openapi/kiota|api-development|OS|1|0|OpenAPI client generator from Microsoft
Hey API|https://heyapi.dev|api-development|OS|1|0|OpenAPI to TypeScript codegen
Jira Product Discovery|https://www.atlassian.com/software/jira/product-discovery|project-management|FT|0|0|Product idea prioritisation
Jira Service Management|https://www.atlassian.com/software/jira/service-management|issue-tracking,project-management|FT|0|0|ITSM and request management
Opsgenie|https://www.atlassian.com/software/opsgenie|monitoring-observability,team-communication|TR|0|0|On-call and alerting
PagerDuty|https://www.pagerduty.com|monitoring-observability,team-communication|TR|0|0|Digital operations management
Incident.io|https://incident.io|monitoring-observability,team-communication|TR|0|0|Incident response platform
FireHydrant|https://firehydrant.com|monitoring-observability|TR|0|0|Incident management
Rootly|https://rootly.com|monitoring-observability|TR|0|0|AI-native incident management
Grafana OnCall|https://grafana.com/oss/oncall/|monitoring-observability|OS|1|0|Open source on-call management
Keep HQ|https://www.keephq.dev|monitoring-observability|OS|1|0|Open source AIOps alert management
Coralogix|https://coralogix.com|monitoring-observability|TR|0|0|Stateful streaming observability
Logz.io|https://logz.io|monitoring-observability|TR|0|0|Open source based observability platform
Sumo Logic|https://www.sumologic.com|monitoring-observability|TR|0|0|Cloud log analytics
Splunk Cloud|https://www.splunk.com|monitoring-observability|TR|0|0|Search and observability platform
Cribl|https://cribl.io|monitoring-observability,data-engineering|TR|0|0|Observability pipeline
Vector.dev|https://vector.dev|monitoring-observability,data-engineering|OS|1|0|Observability data pipeline
Fluentd|https://www.fluentd.org|monitoring-observability,data-engineering|OS|1|0|Unified logging layer
Fluent Bit|https://fluentbit.io|monitoring-observability|OS|1|0|Lightweight log processor and forwarder
Logstash|https://www.elastic.co/logstash|monitoring-observability|OS|1|0|Server-side data processing pipeline
Graylog|https://graylog.org|monitoring-observability|OS|1|0|Log management platform
Seq Logging|https://datalust.co/seq|monitoring-observability|FT|0|0|Structured log server
Papertrail|https://www.papertrail.com|monitoring-observability|FT|0|0|Cloud-hosted log management
Axiom|https://axiom.co|monitoring-observability,analytics|FT|0|0|Log analytics and event database
Tinybird|https://www.tinybird.co|data-engineering,analytics|FT|0|1|Realtime analytics on ClickHouse
Materialize|https://materialize.com|data-engineering,database|FT|0|1|Operational data warehouse
RisingWave|https://risingwave.com|data-engineering|OS|1|0|Streaming database
Apache Pinot|https://pinot.apache.org|data-engineering,database|OS|1|0|Realtime distributed OLAP datastore
Apache Druid|https://druid.apache.org|data-engineering,database|OS|1|0|Realtime analytics database
StarRocks|https://www.starrocks.io|data-engineering,database|OS|1|0|High-performance analytical database
Trino|https://trino.io|data-engineering,database|OS|1|0|Distributed SQL query engine
PrestoDB|https://prestodb.io|data-engineering|OS|1|0|Distributed SQL query engine
Apache Hive|https://hive.apache.org|data-engineering|OS|1|0|Data warehouse software
Apache Iceberg|https://iceberg.apache.org|data-engineering|OS|1|0|Open table format for huge analytic datasets
Delta Lake|https://delta.io|data-engineering|OS|1|0|Open storage layer for lakehouses
Apache Hudi|https://hudi.apache.org|data-engineering|OS|1|0|Incremental data processing framework
dbt Cloud|https://www.getdbt.com/product/dbt-cloud|data-engineering|FT|0|0|Hosted analytics engineering
Elementary Data|https://www.elementary-data.com|data-engineering,testing|OS|1|0|Data observability for dbt
Datafold|https://www.datafold.com|data-engineering,testing|TR|0|0|Data diff and CI for warehouses
Metaplane|https://www.metaplane.dev|data-engineering|TR|0|0|Data observability
Bigeye|https://www.bigeye.com|data-engineering|TR|0|0|Data quality monitoring
Anomalo|https://www.anomalo.com|data-engineering|TR|0|0|Automated data quality
Mintlify|https://mintlify.com|documentation|FT|0|0|Beautiful documentation for developers
ReadMe|https://readme.com|documentation,api-development|TR|0|0|API docs and developer hubs
GitBook|https://www.gitbook.com|documentation,knowledge-base|FT|0|0|Modern documentation platform
Nextra|https://nextra.site|documentation|OS|1|0|Next.js documentation framework
Docsify|https://docsify.js.org|documentation|OS|1|0|Documentation site generator
mdBook|https://rust-lang.github.io/mdBook/|documentation|OS|1|0|Create books from Markdown
Sphinx|https://www.sphinx-doc.org|documentation|OS|1|0|Python documentation generator
TypeDoc|https://typedoc.org|documentation|OS|1|0|TypeScript documentation generator
Compodoc|https://compodoc.app|documentation|OS|1|0|Documentation tool for Angular
Storybook|https://storybook.js.org|ui-ux,documentation,testing|OS|1|0|Frontend workshop for UI components
Histoire|https://histoire.dev|ui-ux,documentation|OS|1|0|Vite-based component workshop
Ladle|https://ladle.dev|ui-ux,documentation|OS|1|0|Fast Storybook alternative
Chromatic|https://www.chromatic.com|ui-ux,testing|FT|0|0|Visual testing for Storybook
Percy|https://percy.io|testing,ui-ux|FT|0|0|Visual testing and review
Applitools|https://applitools.com|testing,ui-ux|TR|0|0|Visual AI testing platform
Lost Pixel|https://lost-pixel.com|testing,ui-ux|OS|1|0|Open source visual regression
Porter|https://porter.run|cloud-hosting,containers|TR|0|0|PaaS on your own cloud
Northflank|https://northflank.com|cloud-hosting,containers|FT|0|0|Developer platform for workloads
Qovery|https://www.qovery.com|cloud-hosting,containers|FT|0|0|Self-service deployment platform
Koyeb|https://www.koyeb.com|cloud-hosting|FT|0|0|Serverless deployment platform
Deno Deploy|https://deno.com/deploy|cloud-hosting|FT|0|0|Edge hosting for Deno apps
Google Cloud Run|https://cloud.google.com/run|cloud-hosting,containers|FT|0|1|Serverless containers on GCP
AWS App Runner|https://aws.amazon.com/apprunner/|cloud-hosting|PD|0|0|Managed container application service
Azure Container Apps|https://azure.microsoft.com/products/container-apps|cloud-hosting,containers|FT|0|0|Serverless containers on Azure
Backstage|https://backstage.io|developer-productivity,documentation,knowledge-base|OS|1|0|Developer portal framework
Port Internal Developer Portal|https://www.getport.io|developer-productivity,knowledge-base|TR|0|0|Internal developer portal
OpsLevel|https://www.opslevel.com|developer-productivity|TR|0|0|Service catalogue and standards
Cortex IDP|https://www.cortex.io|developer-productivity|TR|0|0|Internal developer portal
Humanitec|https://humanitec.com|devops,cloud-hosting|TR|0|0|Internal developer platform
"""


def main() -> None:
    existing = {
        t["name"].lower()
        for p in TOOLS_DIR.glob("*.json")
        for t in json.loads(p.read_text(encoding="utf-8"))
    }
    valid = {
        c["slug"]
        for c in json.loads((DATA / "categories.json").read_text(encoding="utf-8"))
    }

    tools: list[dict] = []
    seen = set(existing)
    for line in EXTRA.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        name, url, cats, st, oss, api, tagline = parts
        cats_list = [c for c in cats.split(",") if c in valid]
        if not cats_list or name.lower() in seen:
            continue
        seen.add(name.lower())
        tools.append(
            make_tool(name, url, cats_list, STATUS_MAP[st], oss == "1", api == "1", tagline)
        )

    out = TOOLS_DIR / "13_extra_developer_stack.json"
    out.write_text(json.dumps(tools, indent=2) + "\n", encoding="utf-8")

    names = [
        t["name"].lower()
        for p in TOOLS_DIR.glob("*.json")
        for t in json.loads(p.read_text(encoding="utf-8"))
    ]
    dups = [n for n, c in Counter(names).items() if c > 1]
    print(f"wrote {len(tools)} -> {out.name}")
    print(f"unique={len(set(names))} total_rows={len(names)} dups={len(dups)}")


if __name__ == "__main__":
    main()
