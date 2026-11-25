const { DmnModdle } = require("dmn-moddle");
const moddle = new DmnModdle();

async function test(ns) {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="${ns}" xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/" xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/" id="Defs_1" name="Test" namespace="http://camunda.org/schema/1.0/dmn">
  <decision id="D01" name="D01">
    <decisionTable id="DT_D01" hitPolicy="UNIQUE">
      <input id="in1"><inputExpression id="ie1" typeRef="number"><text>x</text></inputExpression></input>
      <output id="out1" name="y" typeRef="string" />
      <rule id="r1"><inputEntry id="ie_1"><text>[1..5]</text></inputEntry><outputEntry id="oe_1"><text>"OK"</text></outputEntry></rule>
    </decisionTable>
  </decision>
</definitions>`;
  try {
    const res = await moddle.fromXML(xml);
    console.log(ns, "=> OK, warnings:", res.warnings.length, res.warnings.map(w => w.message));
  } catch (e) {
    console.log(ns, "=> ERR:", e.message);
  }
}

(async () => {
  await test("http://www.omg.org/spec/DMN/20191111/MODEL/");
  await test("https://www.omg.org/spec/DMN/20191111/MODEL/");
})();
