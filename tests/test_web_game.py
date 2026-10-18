import json
import re
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "web" / "index.html"


def run_web_merge(cells, source, target):
    html = HTML.read_text(encoding="utf-8")
    match = re.search(r"function merge\(from,to\)\{([\s\S]*?)\}\n  function renderCatalog", html)
    assert match, "web merge function was not found"
    script = f"""
const state = {{cells: {json.dumps(cells, ensure_ascii=False)}}};
const kinds = {{cabbage: {{category: 'vegetable', maxLevel: 3}}, carrot: {{category: 'vegetable', maxLevel: 3}}, tomato: {{category: 'vegetable', maxLevel: 3}}, pepper: {{category: 'vegetable', maxLevel: 3}}, corn: {{category: 'vegetable', maxLevel: 3}}, chicken: {{category: 'meat', maxLevel: 3}}, beef: {{category: 'meat', maxLevel: 3}}, pork: {{category: 'meat', maxLevel: 3}}, shrimp: {{category: 'meat', maxLevel: 3}}}};
const fusionLv4ById = Object.fromEntries(['cabbage+chicken', 'carrot+beef', 'tomato+shrimp', 'pepper+pork', 'corn+chicken'].map(id => [id, {{id}}]));
const fusionLv5ById = Object.fromEntries(['cabbage+chicken|carrot+beef', 'carrot+beef|tomato+shrimp', 'pepper+pork|tomato+shrimp', 'corn+chicken|pepper+pork', 'cabbage+chicken|corn+chicken'].map(id => [id, {{id}}]));
function fusionParts(recipe) {{ return String(recipe || '').split('|').filter(Boolean).sort(); }}
function canonicalFusionRecipe(recipe) {{ return fusionParts(recipe).join('|'); }}
function discover() {{}}
function merge(from,to) {{{match.group(1)}}}
const result = merge({source}, {target});
console.log(JSON.stringify({{result, cells: state.cells}}));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def run_web_pot(cells, pot_contents, action, index=None):
    html = HTML.read_text(encoding="utf-8")
    move_match = re.search(r"function moveToPot\(index\)\{([\s\S]*?)\}\n  function cookPotContents", html)
    cook_match = re.search(r"function cookPotContents\(\)\{([\s\S]*?)\}\n  function assetFor", html)
    assert move_match and cook_match, "web pot functions were not found"
    script = f"""
const state = {{cells: {json.dumps(cells, ensure_ascii=False)}, potContents: {json.dumps(pot_contents, ensure_ascii=False)}, bagIndex:0, meatBagIndex:1, potIndex:2, discovered:{{}}}};
const potRoutes = [
  {{id:'cabbage+pork',ingredients:['cabbage','pork'],level:4,slots:2}},
  {{id:'carrot+chicken',ingredients:['carrot','chicken'],level:4,slots:2}},
  {{id:'tomato+beef',ingredients:['tomato','beef'],level:4,slots:2}},
  {{id:'pepper+shrimp',ingredients:['pepper','shrimp'],level:4,slots:2}},
  {{id:'corn+pork',ingredients:['corn','pork'],level:4,slots:2}},
  {{id:'cabbage+pork|carrot+chicken',ingredients:['cabbage+pork','carrot+chicken'],level:5,slots:2}},
  {{id:'tomato+beef|pepper+shrimp',ingredients:['tomato+beef','pepper+shrimp'],level:5,slots:2}},
  {{id:'corn+pork|carrot+chicken',ingredients:['corn+pork','carrot+chicken'],level:5,slots:2}},
  {{id:'cabbage+pork|tomato+beef|pepper+shrimp',ingredients:['cabbage+pork','tomato+beef','pepper+shrimp'],level:6,slots:3}},
  {{id:'carrot+chicken|corn+pork|tomato+beef',ingredients:['carrot+chicken','corn+pork','tomato+beef'],level:6,slots:3}}
];
function canonicalFusionRecipe(recipe) {{ return String(recipe || '').split('|').filter(Boolean).sort().join('|'); }}
const potVegetableAliases = {{cabbage:'cabbage',tomato:'tomato',pepper:'pepper',carrot:'carrot',mushroom:'mushroom',corn:'corn',potato:'potato','purple-cabbage':'purple-cabbage'}};
const potMeatAliases = {{sausage:'chicken','chicken-leg':'chicken',bacon:'pork',meatballs:'pork','thick-steak':'beef',ribs:'beef','pork-chop':'pork','roast-roll':'pork','bone-steak':'beef','pork-belly':'pork','roasted-ribs':'beef','meat-feast':'pork'}};
function potIngredientKey(food) {{ if(!food)return ''; if(food.category==='fusion')return canonicalFusionRecipe(food.recipe); if(food.chain)return food.category==='vegetable'?(potVegetableAliases[food.type]||''):(food.category==='meat'?(potMeatAliases[food.type]||''):''); if(food.level!==3)return ''; return food.type; }}
function potRouteForFoods(foods) {{ const keys=foods.map(potIngredientKey).filter(Boolean).sort(); return keys.length===foods.length?potRoutes.find(route=>route.slots===foods.length && route.ingredients.slice().sort().join('|')===keys.join('|')):null; }}
function emptyBoardIndex() {{ return state.cells.findIndex((cell,index)=>cell===null && index!==state.bagIndex && index!==state.meatBagIndex && index!==state.potIndex); }}
function discover() {{}}
function moveToPot(index) {{{move_match.group(1)}}}
function cookPotContents() {{{cook_match.group(1)}}}
const result = {"moveToPot(" + str(index) + ")" if action == "move" else "cookPotContents()"};
console.log(JSON.stringify({{result, cells: state.cells, potContents: state.potContents}}));
"""
    completed = subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(completed.stdout)


def run_web_open_bag():
    html = HTML.read_text(encoding="utf-8")
    add_match = re.search(r"function addFood\(type=randomKind\(\),level=1,chain=[\s\S]*?\)\{([\s\S]*?)\}\n  function discoveryKey", html)
    open_match = re.search(r"function openBag\(category\)\{([\s\S]*?)\}\n  function toast", html)
    assert add_match and open_match, "web bag functions were not found"
    script = f"""
const state = {{cells:[{{kind:'bag',category:'vegetable'}},{{kind:'bag',category:'meat'}},{{kind:'pot'}},null,null,null], bagIndex:0, meatBagIndex:1, potIndex:2, bags:1000, opened:0, meatBags:1000, meatOpened:0}};
const vegetableByType = {{cabbage:{{}}}};
const meatByType = {{'chicken-leg':{{}}}};
function randomKind() {{ return 'cabbage'; }}
function chainFood(type, level, category) {{ return {{category, chain:true, type, level}}; }}
function discover() {{}}
function foodName() {{ return '食材'; }}
function render() {{}}
const messages = [];
function toast(message) {{ messages.push(message); }}
function addFood(type=randomKind(),level=1,chain=vegetableByType[type]!==undefined || meatByType[type]!==undefined,category=meatByType[type]?'meat':'vegetable') {{{add_match.group(1)}}}
function openBag(category) {{{open_match.group(1)}}}
for(let count=0;count<1000;count++) {{ openBag('vegetable'); state.cells[3]=null; }}
const vegetableAtLimit = {{count:state.bags, opened:state.opened}};
openBag('vegetable');
const vegetableAfterLimit = {{count:state.bags, opened:state.opened}};
for(let count=0;count<1000;count++) {{ openBag('meat'); state.cells[3]=null; }}
const meatAtLimit = {{count:state.meatBags, opened:state.meatOpened}};
openBag('meat');
const meatAfterLimit = {{count:state.meatBags, opened:state.meatOpened}};
state.bags=1; state.cells[3]={{type:'tomato'}}; state.cells[4]={{type:'pepper'}}; state.cells[5]={{type:'corn'}};
openBag('vegetable');
const fullBoard = {{count:state.bags, message:messages[messages.length-1]}};
console.log(JSON.stringify({{vegetableAtLimit,vegetableAfterLimit,meatAtLimit,meatAfterLimit,fullBoard}}));
"""
    completed = subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(completed.stdout)


def food(item_type, level=1):
    return {"type": item_type, "level": level}


def test_web_merge_rejects_different_food_types():
    result = run_web_merge([food("tomato"), food("pepper")], 0, 1)
    assert result["result"] == "invalid"
    assert result["cells"] == [food("tomato"), food("pepper")]


def test_web_merge_accepts_same_food_and_increases_level():
    result = run_web_merge([food("tomato"), food("tomato")], 0, 1)
    assert result["result"] == "merged"
    assert result["cells"] == [None, food("tomato", 2)]


def test_web_merge_rejects_same_cell_and_max_level():
    same_cell = run_web_merge([food("tomato")], 0, 0)
    max_level = run_web_merge([food("tomato", 3), food("tomato", 3)], 0, 1)
    assert same_cell["result"] == "invalid"
    assert max_level["result"] == "invalid"


def test_web_merge_vegetables_stop_at_level_three():
    result = run_web_merge([food("tomato", 2), food("tomato", 2)], 0, 1)
    assert result["result"] == "merged"
    assert result["cells"] == [None, food("tomato", 3)]


def test_web_meat_chain_starts_with_chicken_leg_and_merges_to_bacon():
    first = {"category": "meat", "chain": True, "type": "chicken-leg", "level": 1}
    result = run_web_merge([first, first], 0, 1)
    assert result["result"] == "merged"
    assert result["cells"] == [None, {"category": "meat", "chain": True, "type": "bacon", "level": 2}]


def test_web_merge_requires_the_pot_for_cross_category_recipes():
    fusion = lambda recipe, level: {"category": "fusion", "recipe": recipe, "level": level}
    routes = [("cabbage", "pork", "cabbage+pork"), ("carrot", "chicken", "carrot+chicken"), ("tomato", "beef", "tomato+beef"), ("pepper", "shrimp", "pepper+shrimp"), ("corn", "pork", "corn+pork")]
    for vegetable, meat, recipe in routes:
        result = run_web_merge([food(vegetable, 3), food(meat, 3)], 0, 1)
        assert result["result"] == "invalid"
        assert result["cells"] == [food(vegetable, 3), food(meat, 3)]
    unsupported = run_web_merge([food("tomato", 3), food("chicken", 3)], 0, 1)
    assert unsupported["result"] == "invalid"


def test_web_cook_accepts_two_slot_and_three_slot_routes():
    result = run_web_pot([{ "kind": "bag", "category": "vegetable" }, { "kind": "bag", "category": "meat" }, {"kind": "pot"}, food("cabbage", 3), food("pork", 3), None], [], "move", 3)
    assert result["result"]["result"] == "moved"
    assert result["cells"][3] is None and result["potContents"] == [food("cabbage", 3)]
    result = run_web_pot(result["cells"], result["potContents"], "move", 4)
    cooked = run_web_pot(result["cells"], result["potContents"], "cook")
    assert cooked["result"]["result"] == "cooked"
    assert cooked["result"]["food"] == {"category": "fusion", "recipe": "cabbage+pork", "level": 4}
    lv5 = {"category": "fusion", "recipe": "cabbage+pork", "level": 4}
    lv5 = run_web_pot([{"kind":"bag"},{"kind":"bag"},{"kind":"pot"},None,None,None], [lv5,{"category": "fusion", "recipe": "carrot+chicken", "level": 4}], "cook")
    assert lv5["result"]["food"]["level"] == 5
    lv6 = run_web_pot([{"kind":"bag"},{"kind":"bag"},{"kind":"pot"},None,None,None,None], [{"category": "fusion", "recipe": "cabbage+pork", "level": 4}, {"category": "fusion", "recipe": "tomato+beef", "level": 4}, {"category": "fusion", "recipe": "pepper+shrimp", "level": 4}], "cook")
    assert lv6["result"]["food"]["level"] == 6
    chain_result = run_web_pot([{"kind":"bag"},{"kind":"bag"},{"kind":"pot"},{"category": "vegetable", "chain": True, "type": "cabbage", "level": 3}, {"category": "meat", "chain": True, "type": "meatballs", "level": 3}, None], [], "move", 3)
    chain_result = run_web_pot(chain_result["cells"], chain_result["potContents"], "move", 4)
    chain_result = run_web_pot(chain_result["cells"], chain_result["potContents"], "cook")
    assert chain_result["result"]["food"]["recipe"] == "cabbage+pork"


def test_web_pot_accepts_chain_food_aliases_for_named_ingredients():
    cases = [
        ({"category": "vegetable", "chain": True, "type": "cabbage", "level": 1}, {"category": "meat", "chain": True, "type": "meatballs", "level": 3}, "cabbage+pork"),
        ({"category": "vegetable", "chain": True, "type": "carrot", "level": 4}, {"category": "meat", "chain": True, "type": "sausage", "level": 1}, "carrot+chicken"),
        ({"category": "vegetable", "chain": True, "type": "carrot", "level": 4}, {"category": "meat", "chain": True, "type": "chicken-leg", "level": 1}, "carrot+chicken"),
        ({"category": "vegetable", "chain": True, "type": "tomato", "level": 2}, {"category": "meat", "chain": True, "type": "thick-steak", "level": 4}, "tomato+beef"),
        ({"category": "vegetable", "chain": True, "type": "pepper", "level": 3}, food("shrimp", 3), "pepper+shrimp"),
        ({"category": "vegetable", "chain": True, "type": "corn", "level": 6}, {"category": "meat", "chain": True, "type": "bacon", "level": 2}, "corn+pork"),
    ]
    for vegetable, meat, recipe in cases:
        cells = [{"kind": "bag"}, {"kind": "bag"}, {"kind": "pot"}, vegetable, meat, None]
        first = run_web_pot(cells, [], "move", 3)
        second = run_web_pot(first["cells"], first["potContents"], "move", 4)
        assert second["result"]["result"] == "moved"
        cooked = run_web_pot(second["cells"], second["potContents"], "cook")
        assert cooked["result"]["result"] == "cooked"
        assert cooked["result"]["food"]["recipe"] == recipe


def test_web_cook_rejects_invalid_selection_without_consuming():
    cells = [{ "kind": "bag", "category": "vegetable" }, { "kind": "bag", "category": "meat" }, {"kind": "pot"}, food("cabbage", 3), food("pork", 3), None]
    result = run_web_pot(cells, [], "move", 3)
    result = run_web_pot(result["cells"], result["potContents"], "move", 4)
    assert result["result"]["result"] == "moved"
    assert result["cells"][4] is None and result["potContents"] == [food("cabbage", 3), food("pork", 3)]
    invalid = run_web_pot(cells, [food("cabbage", 3), food("pork", 2)], "cook")
    assert invalid["result"]["result"] == "invalid"
    assert invalid["potContents"] == [food("cabbage", 3), food("pork", 2)]
    full = run_web_pot([{ "kind": "bag", "category": "vegetable" }, { "kind": "bag", "category": "meat" }, {"kind": "pot"}, food("cabbage", 3), food("pork", 3), food("tomato", 1)], [food("cabbage", 3), food("pork", 3)], "cook")
    assert full["result"]["result"] == "full"
    assert full["potContents"] == [food("cabbage", 3), food("pork", 3)]


def test_web_page_uses_first_cell_for_bag_and_has_all_assets():
    html = HTML.read_text(encoding="utf-8")
    assert "bagIndex:0" in html
    assert "meatBagIndex:1" in html
    assert "点我开包" not in html
    assert html.count("levels:[") == 9
    for kind in ("cabbage", "carrot", "tomato", "pepper", "corn"):
        for level in range(1, 4):
            assert (ROOT / "web" / "assets" / "foods" / f"{kind}-lv{level}.png").exists()
    assert "cucumber:" not in html
    assert (ROOT / "web" / "assets" / "vegetable-bag-v2.png").exists()


def test_web_page_has_meat_assets_and_independent_bag_counters():
    html = HTML.read_text(encoding="utf-8")
    assert "bags:1000" in html
    assert "meatBags:1000" in html
    assert ">0</b>/1000" in html
    assert "meatOpenedCount" in html
    assert "bag-cell.blocked" in html
    assert "boardHasSpace=emptyBoardIndex()>=0" in html
    assert "棋盘已满，暂不能开包" in html
    assert "randomKind(isMeat?meatKeys:vegetableKeys)" in html
    for kind in ("chicken", "beef", "pork", "shrimp"):
        for level in range(1, 4):
            assert (ROOT / "web" / "assets" / "meats" / f"{kind}-lv{level}.png").exists()
    assert (ROOT / "web" / "assets" / "meat-bag-v1.png").exists()


def test_route_stickers_are_transparent_256px_assets():
    vegetables = ("cabbage", "tomato", "pepper", "carrot", "mushroom", "corn", "potato", "purple-cabbage")
    meats = ("chicken-leg", "bacon", "meatballs", "thick-steak", "ribs", "pork-chop", "roast-roll", "bone-steak", "pork-belly", "roasted-ribs", "meat-feast")
    for folder, names in (("vegetables-sticker", vegetables), ("meats-sticker", meats)):
        for name in names:
            image = Image.open(ROOT / "web" / "assets" / folder / f"{name}.png")
            assert image.mode == "RGBA"
            assert image.size == (256, 256)
            bbox = image.getchannel("A").getbbox()
            assert bbox is not None
            assert min(bbox[0], bbox[1]) >= 8
            assert max(bbox[2], bbox[3]) <= 248
    assert (ROOT / "web" / "assets" / "meats-sticker" / "chicken-leg.png").exists()


def test_web_bags_stop_at_1000_and_board_full_blocks_opening():
    result = run_web_open_bag()
    assert result["vegetableAtLimit"] == {"count": 0, "opened": 1000}
    assert result["vegetableAfterLimit"] == {"count": 0, "opened": 1000}
    assert result["meatAtLimit"] == {"count": 0, "opened": 1000}
    assert result["meatAfterLimit"] == {"count": 0, "opened": 1000}
    assert result["fullBoard"] == {"count": 1, "message": "棋盘已满，请先整理出空位"}


def test_web_page_has_distinct_fusion_assets_and_recipe_rules():
    html = HTML.read_text(encoding="utf-8")
    assert "fusionLv4Routes" in html
    assert "fusionLv5Routes" in html
    assert "这个蔬菜和肉类组合暂未收录" in html
    assert "需要两个不同的 Lv.4 料理" in html
    assert "Lv.5 已是最高料理等级" in html
    assert "level:6" in html
    expected = (
        "fusion-lv4-cabbage-chicken.png", "fusion-lv4-carrot-beef.png", "fusion-lv4-tomato-shrimp.png",
        "fusion-lv4-pepper-pork.png", "fusion-lv4-corn-chicken.png", "fusion-lv5-jade-golden.png",
        "fusion-lv5-sweet-sea.png", "fusion-lv5-rainbow-sea.png", "fusion-lv5-harvest-tower.png",
        "fusion-lv5-jade-corn.png",
    )
    for asset in expected:
        assert (ROOT / "web" / "assets" / "fusions" / asset).exists()
    for asset in (
        "cooking-pot.png", "fusion-pot-lv4-cabbage-pork.png", "fusion-pot-lv4-carrot-chicken.png",
        "fusion-pot-lv4-tomato-beef.png", "fusion-pot-lv4-pepper-shrimp.png", "fusion-pot-lv4-corn-pork.png",
        "fusion-pot-lv5-cabbage-pork--carrot-chicken.png", "fusion-pot-lv5-tomato-beef--pepper-shrimp.png",
        "fusion-pot-lv5-corn-pork--carrot-chicken.png", "fusion-pot-lv6-cabbage-pork--tomato-beef--pepper-shrimp.png",
        "fusion-pot-lv6-carrot-chicken--corn-pork--tomato-beef.png",
    ):
        assert (ROOT / "web" / "assets" / "cooking" / asset).exists()
    assert "potIndex:2" in html
    assert "烹饪锅料理" in html


def test_web_meat_merge_stops_at_level_three():
    result = run_web_merge([food("chicken", 2), food("chicken", 2)], 0, 1)
    blocked = run_web_merge([food("chicken", 3), food("chicken", 3)], 0, 1)
    assert result["result"] == "merged"
    assert result["cells"] == [None, food("chicken", 3)]
    assert blocked["result"] == "invalid"


def test_web_meat_and_vegetable_cannot_merge():
    result = run_web_merge([food("chicken"), food("tomato")], 0, 1)
    assert result["result"] == "invalid"


def test_web_bags_cannot_be_moved_or_merged():
    bag = {"kind": "bag", "category": "vegetable"}
    moved = run_web_merge([bag, None], 0, 1)
    merged = run_web_merge([bag, bag], 0, 1)
    assert moved["result"] == "invalid"
    assert merged["result"] == "invalid"


def test_web_pot_is_fixed_and_cannot_be_moved_or_merged():
    pot = {"kind": "pot"}
    moved = run_web_merge([pot, None], 0, 1)
    merged = run_web_merge([pot, {"type": "tomato", "level": 1}], 0, 1)
    assert moved["result"] == "invalid"
    assert merged["result"] == "invalid"


def test_web_order_and_kind_metadata_cover_both_categories():
    html = HTML.read_text(encoding="utf-8")
    assert "category:'vegetable'" in html
    assert "category:'meat'" in html
    assert "const vegetableKeys" in html
    assert "const meatKeys" in html
    assert "Math.random()<.6?randomKind(vegetableKeys):randomKind(meatKeys)" in html
    assert "kind.maxLevel-1" in html


def test_web_page_contains_catalog_routes():
    html = HTML.read_text(encoding="utf-8")
    for name in ("包菜沙拉", "胡萝卜浓汤", "番茄意面", "彩椒拼盘", "玉米浓汤", "鸡肉汉堡", "牛排", "红烧肉", "海鲜拼盘", "炭香包菜猪肉卷", "胡萝卜鸡腿焗盏", "番茄黑椒牛肉船", "彩椒蒜香虾仁串", "玉米培根黄金杯", "翡翠炭香双拼", "红金海陆焗盘", "金玉炭火丰收盘", "三色炭火盛宴", "金谷海陆铁锅"):
        assert name in html
    assert "catalogBackdrop" in html
    assert "renderCatalog" in html
    assert "手绘料理图鉴" in html
    assert "catalog-recipe" in html
    assert "Lv.${level} · ${slots}槽食谱" in html
    assert "fusionIngredientLabel(route)" in html
    assert "potIngredientLabels" in html
    assert "chicken:'🍗鸡腿'" in html
    assert "renderCatalog(); renderCookingCatalog(); $('catalogBackdrop').classList.add('open')" in html
    assert "touch-action:manipulation" in html
    assert "touch-action:none" in html
    assert "overflow-y:auto" in html
    assert "touch-action:pan-y" in html
    assert "-webkit-overflow-scrolling:touch" in html
    assert "特色料理" in html
    assert "混合料理" not in html
    assert "双味美食" not in html
    assert "皇家宴" not in html


def test_web_page_has_ten_handdrawn_pot_routes():
    html = HTML.read_text(encoding="utf-8")
    route_ids = (
        "cabbage+pork", "carrot+chicken", "tomato+beef", "pepper+shrimp", "corn+pork",
        "cabbage+pork|carrot+chicken", "tomato+beef|pepper+shrimp", "corn+pork|carrot+chicken",
        "cabbage+pork|tomato+beef|pepper+shrimp", "carrot+chicken|corn+pork|tomato+beef",
    )
    for route_id in route_ids:
        assert f"id:'{route_id}'" in html
    cooking_assets = list((ROOT / "web" / "assets" / "cooking").glob("fusion-pot-lv*.png"))
    assert all(asset.exists() for asset in cooking_assets)
    assert len([asset for asset in cooking_assets if asset.name not in {
        "fusion-pot-lv4-garden-wrap.png", "fusion-pot-lv4-golden-beef.png", "fusion-pot-lv4-sea-pasta.png",
        "fusion-pot-lv4-rainbow-skewer.png", "fusion-pot-lv4-corn-cup.png", "fusion-pot-lv5-jade-banquet.png",
        "fusion-pot-lv5-sweet-sea.png", "fusion-pot-lv5-rainbow-platter.png", "fusion-pot-lv6-three-flavor.png",
        "fusion-pot-lv6-harvest-cauldron.png",
    }]) == 10


def test_web_page_explains_different_food_types_cannot_merge():
    html = HTML.read_text(encoding="utf-8")
    assert "function mergeError" in html
    assert "只能合成相同食材" in html
    assert "foodName(a)" in html
    assert "foodName(b)" in html
