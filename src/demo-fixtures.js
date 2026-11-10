import audit from "../public/demo-api/api__automation__audit.json";
import jobs from "../public/demo-api/api__automation__jobs.json";
import playbooks from "../public/demo-api/api__automation__playbooks.json";
import postRun from "../public/demo-api/post__automation__run.json";
import dashboard from "../public/demo-api/api__dashboard__summary.json";
import dbHealth from "../public/demo-api/api__databases__health.json";
import health from "../public/demo-api/api__health.json";
import incidents from "../public/demo-api/api__incidents.json";
import postCorrelate from "../public/demo-api/post__incidents__INC-1043__correlate.json";
import knowledge from "../public/demo-api/api__knowledge.json";
import logEvents from "../public/demo-api/api__logs__events.json";
import postScan from "../public/demo-api/post__logs__scan.json";
import meta from "../public/demo-api/api__meta.json";
import metrics from "../public/demo-api/api__monitoring__metrics.json";
import services from "../public/demo-api/api__monitoring__services.json";
import tickets from "../public/demo-api/api__tickets.json";
import postReport from "../public/demo-api/post__tickets__report.json";
import sla from "../public/demo-api/api__tickets__sla.json";
import vendorDetail from "../public/demo-api/api__vendors__1.json";
import vendors from "../public/demo-api/api__vendors.json";

const GET_FIXTURES = {
  api__meta: meta,
  api__health: health,
  api__dashboard__summary: dashboard,
  api__monitoring__metrics: metrics,
  api__monitoring__services: services,
  api__incidents: incidents,
  api__tickets: tickets,
  api__tickets__sla: sla,
  api__logs__events: logEvents,
  api__automation__playbooks: playbooks,
  api__automation__jobs: jobs,
  api__automation__audit: audit,
  api__databases__health: dbHealth,
  api__vendors: vendors,
  api__vendors__1: vendorDetail,
  api__knowledge: knowledge,
};

const POST_FIXTURES = {
  post__logs__scan: postScan,
  post__tickets__report: postReport,
  post__automation__run: postRun,
  "post__incidents__INC-1043__correlate": postCorrelate,
};

function fixtureKey(path, method) {
  const pathOnly = path.split("?")[0];
  const segments = pathOnly
    .replace(/^\/api\/?/, "")
    .split("/")
    .filter(Boolean);
  const suffix = segments.length ? segments.join("__") : "meta";
  const prefix = method === "GET" || method === "HEAD" ? "api" : "post";
  return `${prefix}__${suffix}`;
}

export function readDemoFixture(path, method = "GET") {
  const key = fixtureKey(path, method);
  const table = method === "GET" || method === "HEAD" ? GET_FIXTURES : POST_FIXTURES;
  const data = table[key];
  if (data === undefined) {
    throw new Error(`Fixture demo ausente: ${method} ${path} (${key})`);
  }
  return structuredClone(data);
}
