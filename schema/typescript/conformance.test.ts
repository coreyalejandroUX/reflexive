// Every shared fixture must get the same verdict here as in the Python kit.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { findUp, validate, type DefName } from "./validate.js";

const fixtures = JSON.parse(readFileSync(findUp("fixtures.json"), "utf8"));

for (const f of fixtures) {
  test(f.name, () => {
    assert.equal(validate(f.doc, f.def as DefName).length === 0, f.valid);
  });
}
