#!/usr/bin/env python3
"""
KSUPA SUP 교육공지 HTML 생성기.

회차마다 바뀌는 값(차수·과정명·일정·장소·접수상태·추가안내)만 받아
assets/announcement-template.html 를 채워 완성 HTML을 출력한다.
고정 정보(시간표·교육비·계좌·문의처·슬로건)는 템플릿에 이미 들어 있다.

사용 예)
  python build_announcement.py \
      --chasu "제49차" \
      --course "SUP 지도자 레벨1 과정" \
      --date "2026년 9월 21일(일) 09:00~18:00" \
      --venue "뚝섬 윈드서핑장 44호 (카이트존스포츠)" \
      --status "신청 접수중" \
      --notice "우천 시 순연됩니다." \
      --out /home/user/go-paddle-homepage/notices/48th-level1.html

--notice 는 여러 번 쓸 수 있고, 생략하면 안내사항 항목이 나타나지 않는다.
--status 는 생략 시 "신청 접수중". 상태에 따라 배지 색이 자동으로 정해진다.
"""
import argparse
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
TEMPLATES = {
    # 완결형 페이지: 파일로 열거나 저장소 페이지로 커밋해 쓰는 용도
    "page": os.path.join(ASSETS, "announcement-template.html"),
    # 붙여넣기용 조각: <style> 없이 인라인 스타일만 — 게시판 HTML 모드에 붙여넣어도 안 깨짐
    "fragment": os.path.join(ASSETS, "announcement-fragment.html"),
}

# 접수 상태별 배지 색 (배경, 글자) — KSUPA 브랜드 팔레트(블루/레드) 기준
STATUS_COLORS = {
    "접수중":   ("#0e86c4", "#ffffff"),  # 브랜드 블루 - 진행중
    "임박":     ("#ed1c24", "#ffffff"),  # 브랜드 레드 - 마감임박
    "마감":     ("#8a9aa6", "#ffffff"),  # 회색 - 접수마감
    "연기":     ("#8a9aa6", "#ffffff"),
    "완료":     ("#8a9aa6", "#ffffff"),
}
DEFAULT_STATUS_COLOR = ("#0e86c4", "#ffffff")


def pick_status_color(status: str):
    for key, color in STATUS_COLORS.items():
        if key in status:
            return color
    return DEFAULT_STATUS_COLOR


def build_notice_block(notices, fmt):
    """추가 안내사항이 있으면 안내 항목 블록을 만든다. 형식에 따라 마크업이 다르다."""
    if not notices:
        return ""
    if fmt == "fragment":
        # 인라인 스타일 버전 (게시판 붙여넣기용)
        items = "\n".join(
            f'          <li style="position:relative;padding-left:16px;font-size:14.5px;'
            f'font-weight:600;color:#082f4a;margin:4px 0;list-style:none;">'
            f'<span style="position:absolute;left:2px;color:#0e86c4;font-weight:800;">·</span>'
            f'{html.escape(n)}</li>'
            for n in notices
        )
        return (
            '<div style="display:flex;padding:16px 0;border-bottom:1px solid #e2ebf1;">\n'
            '      <div style="flex:0 0 auto;width:30px;height:30px;border-radius:9px;background:#ed1c24;'
            'color:#fff;text-align:center;line-height:30px;font-weight:800;font-size:14px;margin-right:14px;">!</div>\n'
            '      <div style="flex:1;"><div style="font-size:12.5px;font-weight:800;color:#5a6b76;'
            'letter-spacing:.04em;margin-bottom:5px;">안내사항</div>\n'
            f'        <ul style="margin:0;padding:0;">\n{items}\n        </ul>\n'
            '      </div>\n'
            '    </div>\n'
        )
    # page 버전 (announcement-template.html 의 CSS 클래스 사용)
    items = "\n".join(f'          <li>{html.escape(n)}</li>' for n in notices)
    return (
        '<div class="item">\n'
        '      <div class="no">!</div>\n'
        '      <div style="flex:1"><div class="c-title">안내사항</div>\n'
        '        <ul class="notice">\n'
        f'{items}\n'
        '        </ul>\n'
        '      </div>\n'
        '    </div>\n'
    )


def main():
    p = argparse.ArgumentParser(description="KSUPA SUP 교육공지 HTML 생성")
    p.add_argument("--chasu", required=True, help='차수, 예: "제49차"')
    p.add_argument("--course", required=True, help='과정명, 예: "SUP 지도자 레벨1 과정"')
    p.add_argument("--date", required=True, help='일정, 예: "2026년 9월 21일(일) 09:00~18:00"')
    p.add_argument("--venue", required=True, help='장소, 예: "뚝섬 윈드서핑장 44호 (카이트존스포츠)"')
    p.add_argument("--status", default="신청 접수중", help='접수 상태 (기본: 신청 접수중)')
    p.add_argument("--notice", action="append", default=[], help="추가 안내사항 (여러 번 사용 가능)")
    p.add_argument("--format", choices=["page", "fragment"], default="page",
                   help='page=완결형 HTML 파일(기본), fragment=게시판 붙여넣기용 인라인 조각')
    p.add_argument("--out", help="저장 경로 (생략 시 표준출력)")
    args = p.parse_args()

    with open(TEMPLATES[args.format], encoding="utf-8") as f:
        tpl = f.read()

    bg, fg = pick_status_color(args.status)
    repl = {
        "{{CHASU}}": html.escape(args.chasu),
        "{{COURSE}}": html.escape(args.course),
        "{{DATE}}": html.escape(args.date),
        "{{VENUE}}": html.escape(args.venue),
        "{{STATUS}}": html.escape(args.status),
        "{{STATUS_BG}}": bg,
        "{{STATUS_FG}}": fg,
        "{{NOTICE_BLOCK}}": build_notice_block(args.notice, args.format),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(tpl)
        print(f"저장 완료: {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(tpl)


if __name__ == "__main__":
    main()
