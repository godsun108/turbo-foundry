import test from "node:test";
import assert from "node:assert/strict";
import { SOULX_ENGLISH_PHONES, validateSoulXPhones } from "../projects/somebodys-gotta-do-it/soulx-phone-inventory.js";

test("accepts documented SoulX English phones", () => {
  assert.deepEqual(validateSoulXPhones(["M","EY1","K"]), []);
  assert.ok(SOULX_ENGLISH_PHONES.has("ZH"));
});

test("rejects empty and unsupported phone tokens", () => {
  assert.equal(validateSoulXPhones([]).length, 1);
  assert.match(validateSoulXPhones(["M","NOT_A_PHONE"])[0], /NOT_A_PHONE/);
});

test("does not silently accept whitespace-padded or lowercase phones", () => {
  assert.equal(validateSoulXPhones([" ey1 "]).length, 1);
  assert.equal(validateSoulXPhones(["ey1"]).length, 1);
});
