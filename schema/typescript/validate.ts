// The TypeScript workspace's reader for schema/reflexive.schema.json.
// Copy this file (or import it) into the workspace; do not copy the schema's
// rules into TypeScript by hand. Same file, same answers as the Python kit:
// schema/typescript/conformance.test.ts checks both against schema/fixtures.json.
import Ajv2020 from "ajv/dist/2020.js";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Find the shared file by walking up from here, so this works from source,
// from a build folder, or copied into the workspace next to a schema/ folder.
export function findUp(name: string, from = dirname(fileURLToPath(import.meta.url))): string {
  for (let dir = from; ; dir = dirname(dir)) {
    for (const candidate of [join(dir, name), join(dir, "schema", name)]) {
      if (existsSync(candidate)) return candidate;
    }
    if (dirname(dir) === dir) throw new Error(`${name} not found above ${from}`);
  }
}

export const schema = JSON.parse(readFileSync(findUp("reflexive.schema.json"), "utf8"));

const ajv = new Ajv2020.default({ allErrors: true });
// x-* keys are Reflexive annotations, not validation keywords.
ajv.addVocabulary(["x-version", "x-corpus-schema", "x-changelog", "x-status", "x-display",
                   "x-allowed-fidelity", "x-allowed-from-phone"]);
ajv.addSchema(schema);

export type DefName = "mobile_envelope" | "mobile_envelope_0_1" | "withdrawal" |
                      "review_item" | "review_decision";

export function validate(doc: unknown, def: DefName): string[] {
  const check = ajv.getSchema(`${schema.$id}#/$defs/${def}`);
  if (!check) throw new Error(`no $def named ${def}`);
  return check(doc) ? [] : (check.errors ?? []).map(e => `${e.instancePath || "/"}: ${e.message}`);
}

export function enumOf(def: string): string[] {
  return [...schema.$defs[def].enum];
}

// Human-facing text for a stored value, e.g. display("support_strength", "no_source").
export function display(def: string, value: string): string {
  return schema.$defs[def]["x-display"]?.[value] ?? value;
}
