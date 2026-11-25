const { evaluate, unaryTest } = require("feelin");

const ctx = {
  dob: "2001-11-25",
  evalDate: "2026-11-25",
  claimDates: ["2024-11-25", "2024-11-24", "2026-12-01", "2025-06-01"],
  perf: "SPORT",
  val: 500000000,
  cc: 250
};

const tests = [
  ["ym_age", 'years and months duration(date(dob), date(evalDate)).years'],
  ["ym_age_before_bday", 'years and months duration(date("2001-11-26"), date("2026-11-25")).years'],
  ["dt_diff", '(date(evalDate) - date(dob)).days'],
  ["age_floor", 'floor((date(evalDate) - date(dob)).days / 365.25)'],
  ["months_btw_exact", 'months between(date("2024-11-25"), date("2026-11-25"))'],
  ["months_btw_1day_over", 'months between(date("2024-11-24"), date("2026-11-25"))'],
  ["dur_sub", 'string(date(evalDate) - duration("P24M"))'],
  ["recent_filter", 'count(claimDates[date(item) >= (date(evalDate) - duration("P24M")) and date(item) <= date(evalDate)])'],
  ["recent_for_filter", 'count((for d in claimDates return if date(d) >= (date(evalDate) - duration("P24M")) and date(d) <= date(evalDate) then 1 else null)[item != null])'],
  ["range_test1", '25 in [17..24]'],
  ["range_test2", '24 in [17..24]'],
  ["list_mem", 'perf in ["SPORT", "HIGH_PERFORMANCE"]'],
  ["builtin_max", 'max(150000, val * 0.005)'],
  ["compound_if", 'if perf in ["SPORT", "HIGH_PERFORMANCE"] and cc > 200 then "HIGH" else "MEDIUM"'],
  ["unary_range", unaryTest('[17..24]', 24)],
  ["unary_open", unaryTest('(150..250]', 150)]
];

for (const item of tests) {
  if (typeof item[1] === "boolean") {
    console.log(item[0], "=>", item[1]);
    continue;
  }
  try {
    console.log(item[0], "=>", JSON.stringify(evaluate(item[1], ctx)));
  } catch (e) {
    console.log(item[0], "ERR:", e.message);
  }
}
