#!/usr/bin/env python3
"""新模块数据准备：把已经落地的素材档案整理成 assets-raw 下的模块数据（本脚本不访问外网）。

公开来源由 scripts/fetch-modules.py 下载后再调用本脚本。私有档案路径仍然可用。

来源：
- 表情：仅当快照里已有 catalog.json 时生成。WaveSpeed 画廊没有公开、可再分发的图包，
  fetch-modules.py 会跳过，不会去抓站。
- CharaDB：items_public.json（标签与日文名 CC0）。有 char-db-cn / anhao 中文层快照时沿用原汉化；
  没有时条目标题用上游日文名。图片只写原站热链，不复制。
- Shisei 历代服饰 + 场景/光影/道具/家具：图片与元数据 CC0 1.0。顺手拷贝 LICENSE-images 与 NOTICE。

用法：
  python3 scripts/prep-modules.py [--archive DIR] [--snapshots DIR] [--raw DIR]
默认 archive=~/workspace/posewear-assets-archive，snapshots=~/workspace/.tmp/pw-modules，
raw=$POSEWEAR_RAW 或 ./assets-raw。产物：<raw>/{expression,charadb,dynasty,scene,light,prop,furn}/
"""
import json, os, re, shutil, sys

HOME = os.path.expanduser('~')
ARC = SNAP = RAW = None  # main() 里定
MISS = []

def cp(src, dst):
    if not os.path.exists(src):
        MISS.append(src); return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not (os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src)):
        shutil.copyfile(src, dst)

def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# ================= 表情（WaveSpeed，汉化） =================
EMO_ZH = {'happy': '开心', 'laughing': '大笑', 'sad': '悲伤', 'angry': '愤怒', 'surprised': '惊讶',
          'scared': '恐惧', 'disgusted': '厌恶', 'smug': '得意', 'flirty': '撩人', 'confused': '困惑',
          'tired': '疲惫', 'silly': '搞怪', 'serious': '严肃', 'shy': '害羞'}
INT_ZH = {'subtle': '含蓄', 'strong': '强烈'}
NAME_ZH = {
 'angry-024': '怒视', 'angry-025': '怒吼', 'angry-026': '龇牙咆哮', 'angry-027': '咬牙切齿',
 'angry-028': '不耐烦', 'angry-029': '挫败', 'angry-030': '暴怒', 'angry-031': '压怒斜视',
 'confused-065': '困惑', 'confused-066': '思考', 'confused-067': '怀疑', 'confused-068': '犹疑·一',
 'confused-069': '犹疑·二', 'confused-070': '专注思索', 'confused-071': '尴尬咧嘴',
 'disgusted-046': '厌恶', 'disgusted-047': '作呕', 'disgusted-048': '轻蔑', 'disgusted-049': '厌腻·强',
 'disgusted-050': '厌腻·弱', 'disgusted-051': '翻白眼',
 'flirty-058': '眨眼', 'flirty-059': '噘嘴', 'flirty-060': '含羞仰视', 'flirty-061': '朦胧眼',
 'flirty-062': '咬唇笑', 'flirty-063': '回眸', 'flirty-064': '飞吻',
 'happy-001': '浅笑', 'happy-002': '暖笑', 'happy-003': '露齿大笑', 'happy-004': '笑容满面',
 'happy-005': '歪头微笑', 'happy-006': '兴奋', 'happy-007': '闭眼满足', 'happy-008': '自豪',
 'laughing-009': '开怀大笑', 'laughing-010': '仰头大笑', 'laughing-011': '抿嘴轻笑', 'laughing-012': '转头大笑',
 'laughing-013': '低笑', 'laughing-014': '笑哭', 'laughing-015': '歪嘴笑',
 'sad-016': '低落', 'sad-017': '含泪噘嘴', 'sad-018': '哭泣', 'sad-019': '别脸难过',
 'sad-020': '强忍眼泪', 'sad-021': '失望', 'sad-022': '悲恸', 'sad-023': '惆怅',
 'scared-039': '恐惧', 'scared-040': '惊恐尖叫', 'scared-041': '紧张', 'scared-042': '担忧',
 'scared-043': '咬唇焦虑', 'scared-044': '缩瑟', 'scared-045': '吓呆',
 'serious-084': '无表情', 'serious-085': '专注凝视', 'serious-086': '坚定', 'serious-087': '严厉',
 'serious-088': '闭目平静', 'serious-089': '倾听', 'serious-090': '侧脸凝视',
 'shy-091': '羞涩微笑', 'shy-092': '尴尬', 'shy-093': '腼腆', 'shy-094': '局促', 'shy-095': '偷偷仰望',
 'silly-078': '鼓腮', 'silly-079': '鱼嘴', 'silly-080': '斗鸡眼', 'silly-081': '鸭子嘴',
 'silly-082': '傻笑', 'silly-083': '夸张震惊',
 'smug-052': '坏笑', 'smug-053': '自鸣得意', 'smug-054': '挑眉坏笑', 'smug-055': '自信',
 'smug-056': '狡黠斜视', 'smug-057': '得意咧嘴',
 'surprised-032': '倒吸气', 'surprised-033': '小惊讶', 'surprised-034': '惊掉下巴', 'surprised-035': '惊喜',
 'surprised-036': '受惊·轻', 'surprised-037': '受惊·重', 'surprised-038': '惊叹',
 'tired-072': '困倦', 'tired-073': '打哈欠', 'tired-074': '无聊', 'tired-075': '精疲力尽',
 'tired-076': '无感', 'tired-077': '打盹'}
DESC_ZH = {
 'angry-024': '从压低的眉毛下怒视，嘴唇紧抿', 'angry-025': '愤怒地喊叫，嘴张大露出牙齿，眉毛用力压低',
 'angry-026': '咆哮状，鼻子皱起，上唇卷起，露出一侧牙齿', 'angry-027': '咬紧牙关发怒，嘴唇向后拉，眉头紧锁',
 'angry-028': '不耐烦地看向一侧，眉毛压低，嘴唇抿成一条线', 'angry-029': '挫败感，嘴唇用力抿紧，眉头拧在一起',
 'angry-030': '暴怒，眼睛在压低的眉毛下瞪大，露出牙齿', 'angry-031': '强压怒火的斜视，头转过去，眼睛从压低的眉毛下斜瞪',
 'confused-065': '一边眉毛抬起一边压低，嘴扯向一侧，头微微歪着', 'confused-066': '抬眼望向别处思考，嘴唇抿着扯向一侧',
 'confused-067': '一边眉毛高抬，另一只眼眯起，嘴唇抿紧', 'confused-068': '犹疑，嘴唇噘起推向一侧，目光瞟开',
 'confused-069': '犹疑，嘴唇噘起推向一侧，目光移开', 'confused-070': '用力专注，眉毛压低并拢，眼睛眯起',
 'confused-071': '尴尬地咧嘴，嘴角横向拉开，眉毛抬起',
 'disgusted-046': '厌恶，鼻子皱起，上唇抬起，眉毛压低', 'disgusted-047': '恶心作呕，嘴张开下坠，鼻子皱起，眼睛眯起',
 'disgusted-048': '轻蔑，一侧嘴角上扯，下巴抬起', 'disgusted-049': '强烈的厌腻，嘴唇卷起，鼻子深深皱起',
 'disgusted-050': '厌腻，嘴唇噘起抿紧，鼻子微微皱起', 'disgusted-051': '翻白眼，眼睛向上翻，嘴唇抿平',
 'flirty-058': '一只眼睛眨动，带着俏皮的微笑', 'flirty-059': '俏皮地噘嘴，嘴唇向前推，眼睛柔和地垂下',
 'flirty-060': '含羞地低着头，从下往上看，带一丝微笑', 'flirty-061': '眼皮半垂的朦胧眼神，淡淡微笑，嘴唇微张',
 'flirty-062': '轻咬下唇，带着一点笑意，眼睛半垂', 'flirty-063': '越过肩膀回头一瞥，带一点微笑',
 'flirty-064': '送飞吻，嘴唇噘起，眼睛几乎闭上',
 'happy-001': '轻轻的闭嘴微笑，脸颊微微抬起，眼睛放松', 'happy-002': '温暖友好的微笑，笑意到达眼睛，脸颊抬起，眼睛轻轻眯起',
 'happy-003': '大大的露齿笑，上下牙都露出来，脸颊高高抬起，眼睛笑成缝', 'happy-004': '大大的闭嘴灿烂笑容，脸颊顶起，眼睛弯成月牙',
 'happy-005': '温柔的微笑，头歪向一侧，柔和亲切', 'happy-006': '兴奋的张嘴笑，眼睛睁大，眉毛抬起',
 'happy-007': '满足的微笑，眼睛安详地闭着，下巴微微抬起', 'happy-008': '自豪的闭嘴微笑，下巴抬起',
 'laughing-009': '张大嘴开怀大笑，露出牙齿，眼睛被脸颊挤起', 'laughing-010': '仰头大笑，眼睛几乎闭上，嘴张得很大',
 'laughing-011': '低头歪头轻笑，嘴唇微微张开，眼睛弯起', 'laughing-012': '转头看向别处大笑，嘴张开，眼睛笑眯眯',
 'laughing-013': '闭嘴低笑，嘴唇抿成宽宽的笑，脸颊鼓起', 'laughing-014': '笑到流泪，眼睛几乎挤闭，眉毛中间抬起，嘴张得很大',
 'laughing-015': '歪着嘴笑，一边嘴角更高，微微露齿',
 'sad-016': '神情低落，内侧眉毛抬起，嘴角下垂，眼睛向下看', 'sad-017': '快要哭出来，下唇向上噘起，内侧眉毛上提',
 'sad-018': '放声哭泣，嘴张开下坠，眼睛挤紧，内侧眉毛高抬', 'sad-019': '难过地别开脸，内侧眉毛抬起，嘴角下垂',
 'sad-020': '强忍眼泪，嘴唇紧抿发抖，下巴皱起，内侧眉毛高抬', 'sad-021': '失望的表情，嘴唇抿着下垂，眼睛垂下',
 'sad-022': '悲恸，眼睛闭着，头低下，眉毛中间上提，嘴角下垂', 'sad-023': '惆怅苦乐参半的神情，悲伤抬起的眉毛下带着淡淡微笑',
 'scared-039': '恐惧，眼睛睁大，眉毛抬起并拢，嘴向后拉开', 'scared-040': '惊恐尖叫，嘴拉得大开，眼睛瞪圆',
 'scared-041': '紧张地看向一侧，眉毛中间抬起，嘴唇拉紧', 'scared-042': '担忧，眉头拧起、中间抬高，嘴绷紧',
 'scared-043': '焦虑地咬着下唇，内侧眉毛抬起', 'scared-044': '疼得缩瑟，眼睛挤紧，脸皱成一团，头转开',
 'scared-045': '吓呆了，瞪大眼睛直视，眉毛抬起，嘴唇微张',
 'serious-084': '中性放松的表情，嘴闭着，眼睛直视前方', 'serious-085': '专注，眉毛微微压低，眼睛眯起',
 'serious-086': '坚定，下巴绷紧，嘴唇抿着，眉毛压低', 'serious-087': '严厉，眉毛压低硬视，嘴角下垂',
 'serious-088': '平静安详，眼睛闭着，面部放松', 'serious-089': '专心倾听，头微微转过去并歪着',
 'serious-090': '头转成 3/4 侧，平静稳定地注视镜头',
 'shy-091': '羞涩的微笑，头低着歪向一侧，眼睛向下看', 'shy-092': '尴尬，紧绷地咧嘴笑，转开脸',
 'shy-093': '腼腆，小小的抿嘴笑，眼睛垂下', 'shy-094': '局促，嘴唇拉平抿紧，眼睛飘开',
 'shy-095': '低着头羞涩地向上偷看，带一点微笑',
 'silly-078': '腮帮鼓起憋着气，眼睛睁大', 'silly-079': '鱼嘴脸，嘴唇推成紧紧的 O 形，眼睛睁大',
 'silly-080': '斗鸡眼的搞怪脸，带着傻笑', 'silly-081': '自拍鸭子嘴，眉毛抬起',
 'silly-082': '傻乎乎的笑，一只眼睛挤闭，嘴扯向一边', 'silly-083': '夸张的卡通震惊脸，下巴掉到最低',
 'smug-052': '一边嘴角抬起的坏笑，眼睛微微眯起', 'smug-053': '自鸣得意，眼睛半闭，闭嘴微笑，下巴抬起',
 'smug-054': '一边眉毛高高挑起，带着了然的坏笑', 'smug-055': '安静的自信，淡淡的闭嘴微笑，下巴微微抬起',
 'smug-056': '狡黠的斜视，半带微笑，头转过去眼睛往回看', 'smug-057': '得意的歪嘴咧笑，一边眉毛抬起',
 'surprised-032': '吃惊倒吸气，眉毛猛地抬起，眼睛睁大，嘴张开', 'surprised-033': '轻微惊讶，眉毛抬起，眼睛稍睁大，嘴唇微张',
 'surprised-034': '震惊到下巴掉下来，嘴大张着，眼睛瞪得很大', 'surprised-035': '愉快的惊喜，张嘴笑，眉毛抬起，眼睛睁大',
 'surprised-036': '微微受惊，头轻轻后缩，眼睛睁大', 'surprised-037': '受惊，头往后缩，眼睛睁大，嘴横向拉开',
 'surprised-038': '惊叹，抬头望，眉毛抬起，嘴微微张开',
 'tired-072': '困倦，眼皮垂下一半，面部松弛', 'tired-073': '大大的哈欠，嘴张得很大，眼睛挤得半闭',
 'tired-074': '无聊，眼皮沉重，嘴推向一侧，看向别处', 'tired-075': '精疲力尽，眼睛耷拉，嘴微微张着',
 'tired-076': '毫无兴趣，平直的注视，眼皮压低，嘴唇抿着', 'tired-077': '打瞌睡，眼睛闭着，头歪向一侧垂下'}
DESC_EN_FILL = {  # 上游 catalog 里 desc 为空的 4 条，按名称补
 'confused-068': 'doubtful, the lips pursed and pushed to one side, glancing away',
 'confused-071': 'an awkward grimace, the mouth stretched sideways and the brows raised',
 'disgusted-049': 'strong distaste, the lips curled, the nose wrinkled hard and the brows lowered',
 'surprised-036': 'startled, the head pulled back slightly, the eyes wide and the brows raised'}

EXPR_SKIP = (
    'prep-modules: 跳过表情。WaveSpeed AI Emotion Gallery 的成图、名称和表情目录没有公开的可再分发包；'
    'https://wavespeed.ai/robots.txt 写明这些图片和数据不是开源的，服务条款第 8.5 节禁止抓取、镜像或复制站点数据。'
    '底层 ICT-FaceKit 是 MIT，但画廊成图不属于该许可。脚本不会绕过限制去抓。')

def keep_shisei_licence(dst):
    for name in ('LICENSE-images', 'NOTICE'):
        src = f'{ARC}/shisei/{name}'
        if os.path.exists(src):
            cp(src, os.path.join(dst, name))

def prep_expression():
    catp = f'{SNAP}/expression/catalog.json'
    if not os.path.exists(catp):
        print(EXPR_SKIP)
        return 0
    cat = json.load(open(catp))
    out = []
    for iid, v in cat.items():
        emo = v['category']
        fn, tq = f'{iid}_front.webp', f'{iid}_three-quarter.webp'
        for f in (fn, tq):
            cp(f'{ARC}/expression/{f}', f'{RAW}/expression/files/w300/{f}')
            cp(f'{ARC}/expression/{f}', f'{RAW}/expression/files/w900/{f}')
        out.append({'id': iid, 'cat': EMO_ZH[emo], 'ti': NAME_ZH[iid], 'zh': DESC_ZH[iid],
                    'en': v['desc'] or DESC_EN_FILL[iid], 'ja': v['name'],
                    'line': EMO_ZH[emo], 'lineEn': emo,
                    'views': {'front': fn, 'tq': tq},
                    'extra': {'emo': EMO_ZH[emo], 'emoEn': emo, 'int': INT_ZH[v['intensity']],
                              'intEn': v['intensity'], 'code': v['code']}})
    dump(out, f'{RAW}/expression/data.json')
    cp(f'{SNAP}/expression/catalog.json', f'{RAW}/expression/source/catalog.json')
    return len(out)

# ================= CharaDB（元数据自存，图片热链） =================
CH = 'https://charadb-2fi.pages.dev'
COLOR_ZH = {'black': '黑', 'blonde': '金', 'pink': '粉', 'silver': '银白', 'brown': '棕'}
CATEN = {'制服与校园风': 'school uniforms', '春夏休闲': 'spring & summer casual', '秋冬休闲': 'autumn & winter casual',
         '职业与角色扮演': 'occupations & cosplay', '泳装': 'swimwear', '奇幻': 'fantasy',
         '礼服与派对': 'dresses & party', '节庆与季节': 'events & seasonal', '通勤与职场': 'commute & office',
         '和服': 'kimono', '运动': 'sports', '居家与睡衣': 'loungewear & pajamas',
         '洛丽塔与地雷系': 'lolita & jirai', '偶像与舞台': 'idol & stage', '军事与科幻': 'military & sci-fi'}

# 官方日文分类 → 本仓库已有的中文类名。条目标题仍用 CC0 日文名，不借用未授权的第三方译文。
HAIR_CAT = {'髪型': '发型', '前髪': '刘海', '髪色': '发色', '髪飾り': '发饰', '目の色': '瞳色', '瞳の形': '瞳型'}
OUTFIT_CAT = {
    '制服・学生': ('制服与校园风', 'school uniforms'),
    'カジュアル(春夏)': ('春夏休闲', 'spring & summer casual'),
    'カジュアル(秋冬)': ('秋冬休闲', 'autumn & winter casual'),
    '職業・コスプレ': ('职业与角色扮演', 'occupations & cosplay'),
    '水着': ('泳装', 'swimwear'),
    'ファンタジー': ('奇幻', 'fantasy'),
    'ドレス・パーティ': ('礼服与派对', 'dresses & party'),
    'イベント・季節': ('节庆与季节', 'events & seasonal'),
    'きれいめ・オフィス': ('通勤与职场', 'commute & office'),
    '和服': ('和服', 'kimono'),
    'スポーツ・部活': ('运动', 'sports'),
    '部屋着・パジャマ': ('居家与睡衣', 'loungewear & pajamas'),
    'ゴスロリ・地雷系': ('洛丽塔与地雷系', 'lolita & jirai'),
    'アイドル・ステージ': ('偶像与舞台', 'idol & stage'),
    'ミリタリー・SF': ('军事与科幻', 'military & sci-fi')}

def _hair_public(items):
    """没有中文层时：标题用 CC0 日文名，分类用上面的中文类名，图片只热链。"""
    styles = [x for x in items if x['set'] == 'hair' and x['sub'] == 'style']
    kids = {}
    for x in items:
        if x.get('sub') == 'style_color':
            kids.setdefault(x['parent'], []).append(x)
    hair = []
    for s in styles:
        vs = [s] + sorted(kids.get(s['id'], []), key=lambda x: x['id'])
        angs = []
        for v in vs:
            cen = v['color'].split()[0]
            angs.append({'zh': COLOR_ZH.get(cen, cen) + '发', 'en': v['color'],
                         't': f"{CH}/thumb/{v['id']}.webp", 'i': f"{CH}/img/{v['id']}.jpg", 'o': ''})
        hair.append({'id': s['id'], 'cat': '发型', 'ti': s['jp'], 'zh': s['jp'], 'en': s['tags'], 'kw': s['tags'],
                     'ja': s['jp'], 'line': '发型', 'lineEn': 'hairstyle', 'no': s['id'], 'ext': 1, 'angles': angs})
    order = ['刘海', '发色', '发饰', '瞳色', '瞳型']
    singles = [x for x in items if x['set'] == 'hair' and x['sub'] in ('bangs', 'color', 'acc', 'eye')]
    singles.sort(key=lambda x: (order.index(HAIR_CAT[x['cat']]), x['id']))
    for x in singles:
        hair.append({'id': x['id'], 'cat': HAIR_CAT[x['cat']], 'ti': x['jp'], 'zh': x['jp'], 'en': x['tags'],
                     'kw': x['tags'], 'ja': x['jp'], 'no': x['id'], 'ext': 1,
                     't': f"{CH}/thumb/{x['id']}.webp", 'm': f"{CH}/img/{x['id']}.jpg", 'i': f"{CH}/img/{x['id']}.jpg", 'o': ''})
    return hair

def _outfits_public(items):
    out = []
    for x in items:
        if x['set'] != 'outfit':
            continue
        zh, en = OUTFIT_CAT[x['cat']]
        tags = [t.strip() for t in x['tags'].split(',') if t.strip()]
        out.append({'id': 'charadb-' + x['id'], 'cat': zh, 'catEn': en, 'kw': x['tags'],
                    'name': x['jp'], 'tagsZh': [x['jp']] + tags,
                    't': f"{CH}/thumb/{x['id']}.webp", 'm': f"{CH}/img/{x['id']}.jpg",
                    'i': f"{CH}/img/{x['id']}.jpg"})
    return out

def prep_charadb():
    src = f'{SNAP}/charadb-shisei/charadb'
    items = json.load(open(f'{src}/items_public.json', encoding='utf-8'))
    cn_path = f'{src}/char-db-cn_data.js'
    az_path = f'{src}/costume-anime-zh_anhao.json'
    if os.path.exists(cn_path):
        js = open(cn_path, encoding='utf-8').read()
        cn = {x['id']: x for x in json.loads(re.search(r'window\.CHARDB=(\{.*\})\s*;?\s*$', js, re.S).group(1))['items']}
        hair = []
        styles = [x for x in items if x['set'] == 'hair' and x['sub'] == 'style']
        kids = {}
        for x in items:
            if x.get('sub') == 'style_color':
                kids.setdefault(x['parent'], []).append(x)
        for s in styles:
            zh = cn[s['id']]['zh']
            vs = [s] + sorted(kids.get(s['id'], []), key=lambda x: x['id'])
            angs = []
            for v in vs:
                cen = v['color'].split()[0]
                angs.append({'zh': COLOR_ZH[cen] + '发', 'en': v['color'],
                             't': f"{CH}/thumb/{v['id']}.webp", 'i': f"{CH}/img/{v['id']}.jpg", 'o': ''})
            hair.append({'id': s['id'], 'cat': '发型', 'ti': zh, 'zh': zh, 'en': s['tags'], 'kw': s['tags'],
                         'ja': s['jp'], 'line': '发型', 'lineEn': 'hairstyle', 'no': s['id'], 'ext': 1, 'angles': angs})
        order = ['刘海', '发色', '发饰', '瞳色', '瞳型']
        singles = [x for x in items if x['set'] == 'hair' and x['sub'] in ('bangs', 'color', 'acc', 'eye')]
        singles.sort(key=lambda x: (order.index(cn[x['id']]['catZh']), x['id']))
        for x in singles:
            c = cn[x['id']]
            hair.append({'id': x['id'], 'cat': c['catZh'], 'ti': c['zh'], 'zh': c['zh'], 'en': x['tags'],
                         'kw': x['tags'], 'ja': x['jp'], 'no': x['id'], 'ext': 1,
                         't': f"{CH}/thumb/{x['id']}.webp", 'm': f"{CH}/img/{x['id']}.jpg", 'i': f"{CH}/img/{x['id']}.jpg", 'o': ''})
    else:
        print('prep-modules: 发型标题用上游 CC0 日文名（char-db-cn 中文层没有可再分发许可，不下载）')
        hair = _hair_public(items)
    dump(hair, f'{RAW}/charadb/hair.json')
    if os.path.exists(az_path):
        az = json.load(open(az_path, encoding='utf-8'))
        out = []
        for x in az:  # anhao 层只有 outfit 440 条，天然不含 outfit2 的 1320 条
            out.append({'id': x['id'], 'cat': x['分类'], 'catEn': CATEN[x['分类']], 'kw': x['关键词'],
                        'name': x['服装名称'], 'tagsZh': x['标签'], 't': x['缩略图'], 'm': x['预览图'],
                        'i': x['原图'], 'sens': bool(x['敏感'])})
        assert len(out) == 440 and all(o['id'].startswith('charadb-O') for o in out)
    else:
        print('prep-modules: 二次元服装标题用上游 CC0 日文名（anhao 中文层没有可再分发许可，不下载）。'
              '公开版不含内衣/性感包，不另标敏感。')
        out = _outfits_public(items)
    dump(out, f'{RAW}/charadb/outfits.json')
    for f in ('items_public.json', 'char-db-cn_data.js', 'costume-anime-zh_anhao.json', 'LICENSE.txt', 'LICENSE'):
        if os.path.exists(f'{src}/{f}'):
            cp(f'{src}/{f}', f'{RAW}/charadb/source/{f}')
    return len(hair), len(out)

# ================= Shisei（CC0，全量自存） =================
VIEW_ORDER = ['front', 'diag', 'side', 'back', 'above', 'below', 'eye', 'tq']
ERA_EN = {'shang': 'Shang dynasty', 'han': 'Han dynasty', 'weijin': 'Wei-Jin period', 'tang': 'Tang dynasty',
          'song': 'Song dynasty', 'yuan': 'Yuan dynasty', 'ming': 'Ming dynasty', 'qing': 'Qing dynasty',
          'rc': 'Republican era', 'wed': 'Wedding'}
SCENE_CAT = {'IN': ('室内', 'Interior'), 'UR': ('城市', 'Urban'), 'NT': ('自然', 'Nature'),
             'HF': ('历史奇幻', 'Historical & fantasy'), 'ST': ('影棚', 'Studio')}
LIGHT_CAT = {'TD': ('时段', 'Time of day'), 'SN': ('空间', 'Space'), 'AR': ('艺术', 'Artistic'),
             'PO': ('人像光位', 'Portrait lighting'), 'FX': ('特效', 'Effects')}
PROP_CAT = {'MU': ('乐器', 'Instruments'), 'CN': ('民族器物', 'Traditional objects'), 'HD': ('手持日用', 'Handheld & daily')}
FURN_CAT = {'SE': ('坐具', 'Seating'), 'TB': ('桌案', 'Tables'), 'CN': ('中式', 'Chinese style'), 'PL': ('影棚结构', 'Studio structures')}

def views_of(it):
    vs = {k: v for k, v in (it.get('views') or {}).items() if v}
    return {k: vs[k] for k in VIEW_ORDER if k in vs}

def prep_dynasty():
    cs = json.load(open(f'{SNAP}/charadb-shisei/shisei/costumes.json'))
    retired = set(cs.get('retired') or [])
    out = []
    for it in cs['items']:
        if it['cat'] != 'HC' or it['id'] in retired:
            continue
        vs = views_of(it)
        if not vs:
            print('prep-modules: 跳过零视角条目 dynasty', it['id']); continue
        for f in vs.values():
            cp(f'{ARC}/shisei/w300/{f}', f'{RAW}/dynasty/files/w300/{f}')
            cp(f'{ARC}/shisei/w900/{f}', f'{RAW}/dynasty/files/w900/{f}')
        out.append({'id': it['id'], 'cat': '历代服饰', 'ti': it['name_zh'], 'zh': it['name_zh'],
                    'en': it['desc_en'], 'ja': it['name_ja'], 'line': it['era_zh'],
                    'lineEn': ERA_EN[it['era']], 'views': vs,
                    'extra': {'era': it['era_zh'], 'eraEn': it['era_en'], 'gender': it['gender']}})
    dump(out, f'{RAW}/dynasty/data.json')
    cp(f'{SNAP}/charadb-shisei/shisei/costumes.json', f'{RAW}/dynasty/source/costumes.json')
    keep_shisei_licence(f'{RAW}/dynasty/source')
    return len(out)

def prep_extra(lib, sub, catmap):
    meta = json.load(open(f'{ARC}/shisei-extra/meta/{lib}.json'))
    retired = set(meta.get('retired') or [])
    out = []
    for it in meta['items']:
        if it['id'] in retired:
            continue
        vs = views_of(it)
        if not vs:
            print('prep-modules: 跳过零视角条目', sub, it['id']); continue
        for f in vs.values():
            cp(f'{ARC}/shisei-extra/{lib}/w300/{f}', f'{RAW}/{sub}/files/w300/{f}')
            cp(f'{ARC}/shisei-extra/{lib}/w900/{f}', f'{RAW}/{sub}/files/w900/{f}')
        cz, cen = catmap[it['cat']]
        ex = {}
        if it.get('dims'):
            d = it['dims']; ex['dims'] = f"{d['w']}×{d['d']}×{d['h']}cm" + (f"，座高 {d['seat']}cm" if d.get('seat') else '')
        if it.get('setting'):
            ex['setting'] = it['setting']
        if it.get('light'):
            ex['light'] = it['light']
        out.append({'id': it['id'], 'cat': cz, 'ti': it['name_zh'], 'zh': it['name_zh'],
                    'en': it['desc_en'], 'ja': it['name_ja'], 'line': it['group_zh'],
                    'lineEn': it['group_en'], 'views': vs, 'extra': ex})
    dump(out, f'{RAW}/{sub}/data.json')
    cp(f'{ARC}/shisei-extra/meta/{lib}.json', f'{RAW}/{sub}/source/{lib}.json')
    keep_shisei_licence(f'{RAW}/{sub}/source')
    return len(out)

def main():
    global ARC, SNAP, RAW
    a = sys.argv[1:]
    def opt(k, d):
        return a[a.index(k) + 1] if k in a else d
    ARC = opt('--archive', f'{HOME}/workspace/posewear-assets-archive')
    SNAP = opt('--snapshots', f'{HOME}/workspace/.tmp/pw-modules')
    RAW = opt('--raw', os.environ.get('POSEWEAR_RAW', 'assets-raw'))
    n = {}
    n['expression'] = prep_expression()
    n['hair'], n['charadb_outfits'] = prep_charadb()
    n['dynasty'] = prep_dynasty()
    n['scene'] = prep_extra('scenes', 'scene', SCENE_CAT)
    n['light'] = prep_extra('lights', 'light', LIGHT_CAT)
    n['prop'] = prep_extra('props', 'prop', PROP_CAT)
    n['furn'] = prep_extra('furniture', 'furn', FURN_CAT)
    if MISS:
        raise SystemExit('缺文件 %d 个：\n%s' % (len(MISS), '\n'.join(MISS[:20])))
    print('prep-modules:', n)

if __name__ == '__main__':
    main()
