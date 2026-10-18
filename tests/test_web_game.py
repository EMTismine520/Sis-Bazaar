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
    assert '<div class="catalog-content" id="catalogContent"></div>' in html
    assert "width:min(480px, calc(100vw - 32px))" in html
    assert "max-width:100%; min-width:0" in html
    assert "overflow:hidden; background:rgba(45,53,45,.45)" in html
    assert "height:min(80vh, 760px)" in html
    assert "max-height:calc(100vh - 28px)" in html
    assert "height:min(80dvh, 760px)" in html
    assert "max-height:calc(100dvh - 28px)" in html
    assert "display:flex; flex-direction:column; overflow:hidden" in html
    assert ".catalog-head { position:sticky; top:0; z-index:2" in html
    assert ".catalog-content { min-height:0; min-width:0; max-width:100%; flex:1 1 auto; overflow-x:hidden; overflow-y:auto" in html
    assert "@media (max-width:600px)" in html
    assert "width:calc(100vw - 20px)" in html
    assert "height:min(78vh, 680px)" in html
    assert "max-height:calc(100vh - 20px)" in html
    assert "height:min(78dvh, 680px)" in html
    assert "max-height:calc(100dvh - 20px)" in html
    assert "$('catalogContent').scrollTop=0" in html
    assert "$('catalogContent').scrollLeft=0" in html
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


def run_web_runtime(case):
    """Run the actual page script, with DOM/storage adapters and real event handlers."""
    harness = r"""
const fs=require('node:fs'), vm=require('node:vm');
const html=fs.readFileSync('web/index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1]
  .replace('(() => {','').replace(/\}\)\(\);\s*$/,'');
const nodes=new Map(), records=new Map(), removedKeys=[];
function element(id='') {
  return {id,dataset:{},className:'',children:[],listeners:{},_html:'',textContent:'',
    get innerHTML(){return this._html;},
    set innerHTML(value){this._html=value;this.children=[];},
    get classList(){const self=this;return {
      add(name){if(!self.className.split(' ').includes(name))self.className+=' '+name;},
      remove(name){self.className=self.className.split(' ').filter(x=>x!==name).join(' ');},
      contains(name){return self.className.split(' ').includes(name);}
    };},
    appendChild(child){child.parent=this;this.children.push(child);},
    contains(child){return child.parent===this;},
    setAttribute(){},setPointerCapture(){},
    insertAdjacentHTML(position,value){this._html+=value;},
    addEventListener(type,handler){this.listeners[type]=handler;},
    closest(selector){
      if(selector==='#'+this.id)return this;
      if(selector.startsWith('.') && selector.slice(1).split('.').every(name=>this.classList.contains(name)))return this;
      return this.parent?.closest(selector)||null;
    }
  };
}
const document={
  getElementById(id){if(!nodes.has(id))nodes.set(id,element(id));return nodes.get(id);},
  createElement(){return element();},addEventListener(){},
  querySelectorAll(){return [...nodes.values()].flatMap(x=>x.children).filter(x=>x.classList.contains('dragging'));},
  elementFromPoint(){return this.hit;}
};
const localStorage={getItem:key=>records.get(key)||null,setItem:(key,value)=>records.set(key,value),removeItem:key=>{records.delete(key);removedKeys.push(key);}};
vm.runInNewContext(script+'\n'+fs.readFileSync(0,'utf8'),{
  document,localStorage,window:{confirm:()=>true},console,records,removedKeys,
  setTimeout:()=>0,clearTimeout:()=>{}
});
"""
    completed = subprocess.run(
        ["node", "-e", harness], input=case, cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_v2_merge_rewards_once_and_locked_levels_keep_ingredients():
    result = run_web_runtime("""
const initial=state.coins;
const merged=merge(3,4), afterMerge=state.coins;
const moved=merge(4,10), afterMove=state.coins;
state.cells[3]=chainFood('pepper',3,'vegetable');
state.cells[4]=chainFood('pepper',3,'vegetable');
const before=JSON.stringify(state.cells), locked=merge(3,4);
const preserved=before===JSON.stringify(state.cells);
buyIngredient('vegetable',4);
const purchased=state.coins, unlockedMerge=merge(3,4);
console.log(JSON.stringify({initial,merged,afterMerge,moved,afterMove,locked,preserved,purchased,unlockedMerge,coins:state.coins,food:state.cells[4]}));
""")
    assert result["merged"] == "merged" and result["afterMerge"] == 123
    assert result["moved"] == "moved" and result["afterMove"] == 123
    assert result["locked"] == "locked" and result["preserved"]
    assert result["purchased"] == 63 and result["coins"] == 66
    assert result["unlockedMerge"] == "merged" and result["food"]["level"] == 4


def test_v2_cooking_rewards_all_levels_without_extra_bags():
    result = run_web_runtime("""
const results=[];
for(const level of [4,5,6]){
  beginNewGame();
  const route=potRoutes.find(route=>route.level===level);
  state.potContents=level===4?[chainFood('cabbage',1,'vegetable'),chainFood('bacon',2,'meat')]:route.ingredients.map(recipe=>({category:'fusion',recipe,level:4}));
  cookSelected();
  results.push({level,coins:state.coins,bags:state.bags,meatBags:state.meatBags,pot:state.potContents.length,discovered:state.discovered[discoveryKey({category:'fusion',recipe:route.id,level})]});
}
console.log(JSON.stringify(results));
""")
    for row in result:
        assert row["coins"] == 120 + row["level"] * 3
        assert row["bags"] == row["meatBags"] == 1000
        assert row["pot"] == 0 and row["discovered"]


def test_v2_unlock_cost_sequence_balance_and_independent_routes():
    result = run_web_runtime("""
const prices=[4,5,6,7,8,9,10,11].map(ingredientUnlockCost);
const sequence=buyIngredient('vegetable',5), afterSequence=state.coins;
const purchased=buyIngredient('vegetable',4), repeat=buyIngredient('vegetable',4);
const poor=buyIngredient('vegetable',5), poorMessage=$('message').textContent;
const independent=state.unlockedLevels.meat;
state.coins=200;const next=buyIngredient('vegetable',5);
const meat=buyIngredient('meat',4);
console.log(JSON.stringify({prices,sequence,afterSequence,purchased,repeat,poor,poorMessage,independent,next,meat,coins:state.coins,unlocked:state.unlockedLevels}));
""")
    assert result["prices"] == [60, 90, 120, 150, 180, 210, 240, 270]
    assert result["sequence"]["result"] == "sequence" and result["afterSequence"] == 120
    assert result["purchased"]["price"] == 60 and result["repeat"]["result"] == "unlocked"
    assert result["poor"]["result"] == "poor" and "金币不足" in result["poorMessage"]
    assert result["independent"] == 3 and result["unlocked"] == {"vegetable": 5, "meat": 4}
    assert result["coins"] == 50


def test_v2_order_failure_success_refresh_and_no_duplicate_reward():
    result = run_web_runtime("""
state.order={...chainFood('cabbage',1,'vegetable'),reward:999};
const before=JSON.stringify(state), failed=submitOrder(8), preserved=before===JSON.stringify(state);
const message=$('message').textContent, oldOrder=state.order;
const success=submitOrder(3), refreshed=state.order!==oldOrder;
const nextValid=orderCandidates().some(food=>sameFood(food,state.order));
const duplicate=submitOrder(3);
console.log(JSON.stringify({failed,preserved,message,success,refreshed,nextValid,duplicate,coins:state.coins,day:state.day,cell:state.cells[3],bags:state.bags,meatBags:state.meatBags,order:state.order}));
""")
    assert result["failed"]["result"] == "invalid" and result["preserved"]
    assert "订单需要" in result["message"]
    assert result["success"] == {"result": "submitted", "reward": 24}
    assert result["refreshed"] and result["nextValid"] and result["duplicate"]["result"] == "invalid"
    assert result["coins"] == 144 and result["day"] == 2 and result["cell"] is None
    assert result["bags"] == result["meatBags"] == 1000


def test_v2_fusion_orders_match_recipe_and_level():
    result = run_web_runtime("""
const route=potLv5Routes[0];
state.order={category:'fusion',recipe:route.id,level:5,reward:orderReward(5)};
state.cells[3]={category:'fusion',recipe:route.ingredients.slice().reverse().join('|'),level:5};
state.cells[4]={category:'fusion',recipe:potLv5Routes[1].id,level:5};
const wrongRecipe=submitOrder(4), success=submitOrder(3);
console.log(JSON.stringify({wrongRecipe,success,coins:state.coins,remaining:state.cells[4]}));
""")
    assert result["wrongRecipe"]["result"] == "invalid" and result["remaining"]
    assert result["success"]["reward"] == 56 and result["coins"] == 176


def test_v2_orders_only_use_discovered_unlocked_foods_and_fallback():
    result = run_web_runtime("""
state.discovered={'cabbage:1':true};
const fallback=newOrder();
buyIngredient('vegetable',4);
state.discovered['tomato:2']=true;
const purchasedOnly=orderCandidates();
state.discovered['thick-steak:4']=true; // Still locked on the meat route.
const route=potLv4Routes[0];state.discovered[discoveryKey({category:'fusion',recipe:route.id,level:4})]=true;
const pool=orderCandidates();
const samples=Array.from({length:200},()=>newOrder());
console.log(JSON.stringify({fallback,purchasedOnly,pool,samples}));
""")
    assert result["fallback"]["type"] == "cabbage"
    assert len(result["purchasedOnly"]) == 2  # Without a discovered dish, orders fall back to discovered basics.
    assert len(result["pool"]) == 4
    expected = {
        (item.get("category"), item.get("type"), item.get("recipe"), item["level"])
        for item in result["pool"]
    }
    sampled = {
        (item.get("category"), item.get("type"), item.get("recipe"), item["level"])
        for item in result["samples"]
    }
    assert sampled <= expected
    assert not any(item.get("type") == "thick-steak" for item in result["pool"])


def test_v2_storage_roundtrip_keeps_entire_progress_and_pot():
    result = run_web_runtime("""
buyIngredient('vegetable',4);openBag('vegetable');openBag('meat');
moveToPot(3);state.day=7;render();
const saved=JSON.parse(localStorage.getItem(SAVE_KEY));
beginNewGame();const restored=loadGame();
const after=JSON.parse(localStorage.getItem(SAVE_KEY));
console.log(JSON.stringify({restored,equal:JSON.stringify(saved)===JSON.stringify(after),after}));
""")
    assert result["restored"] and result["equal"]
    saved = result["after"]
    assert saved["version"] == "2.0.0" and saved["schema"] == 2
    assert saved["coins"] == 60 and saved["day"] == 7
    assert saved["bags"] == saved["meatBags"] == 999
    assert saved["opened"] == saved["meatOpened"] == 1
    assert saved["unlockedLevels"] == {"vegetable": 4, "meat": 3}
    assert saved["cells"][3] is None and len(saved["potContents"]) == 1


def test_v2_corrupt_and_incompatible_saves_start_safely():
    result = run_web_runtime("""
const good=JSON.parse(localStorage.getItem(SAVE_KEY));
const corrupt=[null,{...good,version:'1.0.0'},{...good,schema:1},{...good,cells:[]},{...good,coins:-1},{...good,day:0},{...good,bagIndex:10},{...good,opened:1001},{...good,discovered:[]},{...good,potContents:[{}]}];
const wrongFood=JSON.parse(JSON.stringify(good));wrongFood.cells[3]={type:'missing',level:9};corrupt.push(wrongFood);
const lockedFood=JSON.parse(JSON.stringify(good));lockedFood.cells[3]={category:'vegetable',chain:true,type:'carrot',level:4};corrupt.push(lockedFood);
const results=corrupt.map(value=>{localStorage.setItem(SAVE_KEY,JSON.stringify(value));return loadGame()===false && state.coins===120 && state.day===1;});
localStorage.setItem(SAVE_KEY,'{broken json');results.push(loadGame()===false);
const invalidOrder={...good,coins:99,order:{...chainFood('carrot',4,'vegetable'),reward:48}};
localStorage.setItem(SAVE_KEY,JSON.stringify(invalidOrder));
const restored=loadGame();
console.log(JSON.stringify({results,restored,coins:state.coins,order:state.order}));
""")
    assert all(result["results"])
    assert result["restored"] and result["coins"] == 99
    assert result["order"]["level"] == 1


def test_v2_reset_requires_confirmation_and_replaces_save():
    result = run_web_runtime("""
buyIngredient('meat',4);openBag('meat');
const before=localStorage.getItem(SAVE_KEY);
window.confirm=()=>false;reset();const cancelled=localStorage.getItem(SAVE_KEY)===before && state.coins===60;
window.confirm=()=>true;reset();
console.log(JSON.stringify({cancelled,removed:removedKeys.includes(SAVE_KEY),saved:JSON.parse(localStorage.getItem(SAVE_KEY))}));
""")
    assert result["cancelled"] and result["removed"]
    saved = result["saved"]
    assert saved["coins"] == 120 and saved["day"] == 1
    assert saved["unlockedLevels"] == {"vegetable": 3, "meat": 3}
    assert saved["bags"] == saved["meatBags"] == 1000 and saved["potContents"] == []


def test_v2_pointer_events_pay_once_and_submit_to_order_card():
    result = run_web_runtime("""
function drop(from,target){
  const board=$('board');
  board.listeners.pointerdown({target:board.children[from],pointerId:1});
  document.hit=target;board.listeners.pointerup({clientX:0,clientY:0});
}
drop(3,$('board').children[4]);const mergedCoins=state.coins;
state.order={...chainFood('tomato',2,'vegetable'),reward:orderReward(2)};
drop(4,$('orderCard'));
console.log(JSON.stringify({mergedCoins,coins:state.coins,day:state.day,cell:state.cells[4],saved:JSON.parse(localStorage.getItem(SAVE_KEY)).coins}));
""")
    assert result == {"mergedCoins": 123, "coins": 155, "day": 2, "cell": None, "saved": 155}


def test_v2_page_has_shop_version_order_drop_and_narrow_layout():
    html = HTML.read_text(encoding="utf-8")
    assert "v2.0.0" in html and "const SAVE_SCHEMA=2" in html
    for item_id in ("shopOpen", "shopClose", "shopBackdrop", "shopCoins", "shopContent", "orderCard"):
        assert f'id="{item_id}"' in html
    assert "hit?.closest?.('#orderCard')" in html and "submitOrder(from)" in html
    assert "已解锁 · 未发现" in html and "🔒 未解锁" in html
    assert ".footer { flex-wrap:wrap" in html and "#message { flex-basis:100%" in html
    assert ".shop-content { min-height:0; overflow-y:auto" in html
    assert "localStorage.setItem(SAVE_KEY" in html and "localStorage.removeItem(SAVE_KEY" in html
    assert "window.confirm(" in html and "  loadGame();\n})();" in html
