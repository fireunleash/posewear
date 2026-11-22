#!/usr/bin/env python3
"""把公开、许可允许再分发的新模块素材下载到本地，再调用 prep-modules.py。

会下载：
- Shisei（https://github.com/wquguru/shisei ，commit 见下方常量）
  历代服饰 / 场景 / 光影 / 道具 / 家具的元数据和 w300、w900 图片。
  图片与 data/ 为 CC0 1.0，同时保存 LICENSE-images 和 NOTICE。
- CharaDB（https://github.com/taki-ttt/charadb）的 items_public.json 和 LICENSE。
  标签与日文名是 CC0。图片不下载，prep-modules 只写
  https://charadb-2fi.pages.dev 的热链。

不会下载：
- WaveSpeed 表情图。站点 robots.txt 与服务条款禁止抓取这些图片和数据，
  也没有公开的可再分发包。详见 prep-modules 的跳过说明。
- char-db-cn、anhao/ai-pose-gallery-zh 的中文层。仓库没有把译文授为可再分发。
- CharaDB 的任何图片，包括 Releases 里的 zip 和第三方仓库里的缩略图。

用法：
  python3 scripts/fetch-modules.py
  POSEWEAR_RAW=/path python3 scripts/fetch-modules.py
"""
import json, os, subprocess, sys, time, urllib.request
import concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get('POSEWEAR_RAW', os.path.join(ROOT, 'assets-raw'))
ARC = os.path.join(RAW, '_upstream', 'archive')
SNAP = os.path.join(RAW, '_upstream', 'snapshots')

# 固定到核对过条目数的提交，避免上游 main 一变，本地条数就漂。
SHISEI = '6e22358bab73c51eeae0615030635ace199169f8'
CHARADB = '7fe2e4b009ad6d85496101e929ac8528cb21d357'
SHISEI_RAW = 'https://raw.githubusercontent.com/wquguru/shisei/' + SHISEI + '/'
CHARADB_RAW = 'https://raw.githubusercontent.com/taki-ttt/charadb/' + CHARADB + '/'
UA = {'User-Agent': 'Mozilla/5.0 (PoseWear local build)'}
WORKERS = 6
VIEW_ORDER = ['front', 'diag', 'side', 'back', 'above', 'below', 'eye', 'tq']
# 上游 json 路径、prep-modules 用的库名、图片在仓库里的目录
EXTRAS = [
    ('data/scenes.json', 'scenes', 'images/scene/plain'),
    ('data/lights.json', 'lights', 'images/light/plain'),
    ('data/props.json', 'props', 'images/prop/grey'),
    ('data/furniture.json', 'furniture', 'images/furniture/grey'),
]
EXPECT = {'expression': 0, 'hair': 122, 'charadb_outfits': 440,
          'dynasty': 57, 'scene': 64, 'light': 50, 'prop': 32, 'furn': 41}


def views_of(it):
    vs = {k: v for k, v in (it.get('views') or {}).items() if v}
    return {k: vs[k] for k in VIEW_ORDER if k in vs}


def retired_ids(meta):
    r = meta.get('retired') or []
    return set(r)


def get(url, path=None, tries=4):
    if path and os.path.exists(path) and os.path.getsize(path) > 0:
        return 0
    err = None
    for i in range(tries):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            if path is None:
                return b
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path + '.part', 'wb').write(b)
            os.replace(path + '.part', path)
            return len(b)
        except Exception as e:
            err = e
            time.sleep(1 + i * 2)
    print('失败', url, err, flush=True)
    return None if path is None else 0


def save_bytes(url, path):
    n = get(url, path)
    if not (path and os.path.exists(path) and os.path.getsize(path) > 0):
        sys.exit('下载失败：' + url)
    return n


def save_json_url(url, path):
    save_bytes(url, path)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def image_jobs(meta, img_prefix, dest_dir, only_cat=None):
    jobs = []
    seen = set()
    for it in meta['items']:
        if only_cat and it.get('cat') != only_cat:
            continue
        if it['id'] in retired_ids(meta):
            continue
        for fn in views_of(it).values():
            if fn in seen:
                continue
            seen.add(fn)
            for tier in ('w300', 'w900'):
                url = SHISEI_RAW + img_prefix + '/' + tier + '/' + fn
                dst = os.path.join(dest_dir, tier, fn)
                jobs.append((url, dst))
    return jobs


def fetch_images(jobs):
    done = 0
    nbytes = 0
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        futs = [ex.submit(get, url, dst) for url, dst in jobs]
        for fut in cf.as_completed(futs):
            n = fut.result()
            done += 1
            nbytes += n or 0
            if done % 100 == 0 or done == len(jobs):
                print(f'  图片 {done}/{len(jobs)}  {nbytes / 1e6:.0f} MB', flush=True)
    missing = [url for url, dst in jobs if not (os.path.exists(dst) and os.path.getsize(dst) > 0)]
    if missing:
        sys.exit('缺图片 %d 个，例如：\n%s' % (len(missing), '\n'.join(missing[:8])))


def write_note(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)


def main():
    os.chdir(ROOT)
    print('Shisei', SHISEI)
    print('CharaDB', CHARADB)
    costumes = save_json_url(SHISEI_RAW + 'data/costumes.json',
                             os.path.join(SNAP, 'charadb-shisei', 'shisei', 'costumes.json'))
    jobs = image_jobs(costumes, 'images/costume/grey', os.path.join(ARC, 'shisei'), only_cat='HC')
    extras = {}
    for rel, lib, img in EXTRAS:
        meta = save_json_url(SHISEI_RAW + rel, os.path.join(ARC, 'shisei-extra', 'meta', lib + '.json'))
        extras[lib] = meta
        jobs += image_jobs(meta, img, os.path.join(ARC, 'shisei-extra', lib))
    print(f'需要图片 {len(jobs)} 个（w300+w900）', flush=True)
    fetch_images(jobs)
    for name in ('LICENSE-images', 'NOTICE'):
        save_bytes(SHISEI_RAW + name, os.path.join(ARC, 'shisei', name))
    ch = os.path.join(SNAP, 'charadb-shisei', 'charadb')
    save_bytes(CHARADB_RAW + 'data/items_public.json', os.path.join(ch, 'items_public.json'))
    save_bytes(CHARADB_RAW + 'LICENSE', os.path.join(ch, 'LICENSE.txt'))
    write_note(os.path.join(RAW, 'expression', 'SKIPPED.txt'),
               '表情库没有从公开来源生成。\n\n'
               'WaveSpeed AI Emotion Gallery（https://wavespeed.ai/free-tools/ai-emotion-gallery）'
               '的成图和目录数据没有公开的可再分发包。robots.txt 写明图片、预设和数据归 WaveSpeedAI 所有、'
               '不是开源的，服务条款第 8.5 节禁止抓取或镜像。\n'
               '底层头模 ICT-FaceKit（https://github.com/USC-ICT/ICT-FaceKit）是 MIT，'
               '但画廊成图、名称和 blendshape 目录是 WaveSpeed 做的，不能靠抓站来补。\n'
               '若你自己已有一份合法的本地档案，可以按 scripts/prep-modules.py 的 '
               '--archive / --snapshots 生成，本脚本不会去抓。\n')
    src = {
        'shisei': {'repo': 'https://github.com/wquguru/shisei', 'commit': SHISEI,
                   'licence': 'CC0 1.0 Universal for images/ and data/ (LICENSE-images, NOTICE). Code is Apache-2.0 and is not copied.'},
        'charadb': {'repo': 'https://github.com/taki-ttt/charadb', 'commit': CHARADB,
                    'licence': 'Tag data and Japanese labels: CC0 1.0 (LICENSE section 2). Images are not downloaded; pages hotlink https://charadb-2fi.pages.dev .'},
        'expression': {'skipped': True, 'reason': 'No public redistributable WaveSpeed gallery pack; scraping is prohibited.'},
    }
    write_note(os.path.join(RAW, '_upstream', 'SOURCES.json'), json.dumps(src, ensure_ascii=False, indent=2) + '\n')
    print('运行 prep-modules.py', flush=True)
    subprocess.check_call([sys.executable, os.path.join(ROOT, 'scripts', 'prep-modules.py'),
                           '--archive', ARC, '--snapshots', SNAP, '--raw', RAW])
    counts = {}
    for key, path in (
        ('hair', 'charadb/hair.json'),
        ('charadb_outfits', 'charadb/outfits.json'),
        ('dynasty', 'dynasty/data.json'),
        ('scene', 'scene/data.json'),
        ('light', 'light/data.json'),
        ('prop', 'prop/data.json'),
        ('furn', 'furn/data.json'),
    ):
        with open(os.path.join(RAW, path), encoding='utf-8') as f:
            counts[key] = len(json.load(f))
    counts['expression'] = 0
    exp = os.path.join(RAW, 'expression', 'data.json')
    if os.path.exists(exp):
        with open(exp, encoding='utf-8') as f:
            counts['expression'] = len(json.load(f))
        print('表情：沿用已有的 expression/data.json（%d 条），本脚本没有下载 WaveSpeed。' % counts['expression'])
    # 已有的表情档案可以不是 0。其余模块必须对上这个提交的条数，避免下半截。
    bad = {k: (counts.get(k), EXPECT[k]) for k in EXPECT if k != 'expression' and counts.get(k) != EXPECT[k]}
    if bad:
        sys.exit('条数与锁定的上游提交不一致：' + json.dumps(bad, ensure_ascii=False))
    for sub in ('dynasty', 'scene', 'light', 'prop', 'furn', 'charadb'):
        write_note(os.path.join(RAW, sub, 'source', 'SOURCES.json'), json.dumps(src, ensure_ascii=False, indent=2) + '\n')
    print('fetch-modules:', counts)
    print('表情已跳过。接下来：python3 build.py')


if __name__ == '__main__':
    main()
