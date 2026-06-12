#!/usr/bin/env python3
"""Generate the MMPB-Clean dataset statistics figure as a standalone SVG."""

import argparse
import csv
import html
import math
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_DATASET = Path("../../outputs/cvlmp_eval/v4_name_memory/dataset_name_memory_v4_full.csv")
DEFAULT_OUTPUT = Path("../static/images/mmpb_clean_dataset_stats.svg")


TASK_ORDER = [
    "preference_yesno",
    "preference_mcq",
    "recognition_yesno",
    "recognition_mcq",
]
TASK_LABELS = {
    "preference_yesno": "Preference Yes/No",
    "preference_mcq": "Preference MCQ",
    "recognition_yesno": "Recognition Yes/No",
    "recognition_mcq": "Recognition MCQ",
}
TASK_SHORT_LABELS = {
    "preference_mcq": "Pref.\nMCQ",
    "preference_yesno": "Pref.\nYes/No",
    "recognition_mcq": "Recog.\nMCQ",
    "recognition_yesno": "Recog.\nYes/No",
}
ATTRIBUTE_ORDER = ["human", "animal", "character", "object"]
ATTRIBUTE_LABELS = {
    "human": "Human users",
    "animal": "Animals",
    "character": "Characters",
    "object": "Objects",
}


COLORS = {
    "preference": "#C94FA3",
    "recognition": "#55B96B",
    "preference_yesno": "#D45BB2",
    "preference_mcq": "#9966D9",
    "recognition_yesno": "#55C96F",
    "recognition_mcq": "#65C9CD",
    "human": "#D95D59",
    "animal": "#D5BD54",
    "character": "#56C978",
    "object": "#67C9C9",
    "train": "#4D5FB3",
    "test": "#59C3CD",
    "ink": "#242733",
    "muted": "#6C7180",
    "grid": "#D9DDE8",
}


def load_stats(dataset_path):
    task_counts = Counter()
    category_counts = Counter()
    split_task_counts = Counter()
    identity_names = defaultdict(set)

    rows = 0
    with dataset_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows += 1
            task = row["task_family"]
            category = row["category"]
            split = row["split_v4"]
            attr = row["attribute"]
            name = row["name"]

            task_counts[task] += 1
            category_counts[category] += 1
            split_task_counts[(split, task)] += 1
            identity_names[attr].add(name)

    identity_counts = {k: len(v) for k, v in identity_names.items()}
    total_identities = len(set().union(*identity_names.values()))

    return {
        "rows": rows,
        "task_counts": task_counts,
        "category_counts": category_counts,
        "split_task_counts": split_task_counts,
        "identity_counts": identity_counts,
        "total_identities": total_identities,
    }


def fmt_int(value):
    return f"{value:,}"


def pct(value, total):
    return f"{100 * value / total:.1f}%"


def polar(cx, cy, radius, angle_deg):
    angle = math.radians(angle_deg)
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def donut_path(cx, cy, r_outer, r_inner, start, end):
    if end - start >= 359.99:
        end = start + 359.99

    x1, y1 = polar(cx, cy, r_outer, start)
    x2, y2 = polar(cx, cy, r_outer, end)
    x3, y3 = polar(cx, cy, r_inner, end)
    x4, y4 = polar(cx, cy, r_inner, start)
    large = 1 if end - start > 180 else 0
    return (
        f"M {x1:.3f} {y1:.3f} "
        f"A {r_outer:.3f} {r_outer:.3f} 0 {large} 1 {x2:.3f} {y2:.3f} "
        f"L {x3:.3f} {y3:.3f} "
        f"A {r_inner:.3f} {r_inner:.3f} 0 {large} 0 {x4:.3f} {y4:.3f} Z"
    )


class Svg:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="MMPB-Clean dataset statistics">',
            "<defs>",
            "<style>",
            "text{font-family:'Times New Roman',Times,serif;fill:#242733}",
            ".sans{font-family:Arial,Helvetica,sans-serif}",
            ".title{font-size:28px;font-weight:700}",
            ".caption{font-size:27px;font-weight:700}",
            ".label{font-size:20px}",
            ".small{font-size:16px}",
            ".tiny{font-size:14px}",
            ".muted{fill:#6C7180}",
            ".axis{stroke:#242733;stroke-width:1.5}",
            ".grid{stroke:#D9DDE8;stroke-width:1}",
            "</style>",
            "</defs>",
            '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        ]

    def add(self, raw):
        self.parts.append(raw)

    def text(
        self,
        x,
        y,
        content,
        *,
        cls="",
        anchor="middle",
        size=None,
        weight=None,
        fill=None,
        rotate=None,
    ):
        attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'text-anchor="{anchor}"']
        if cls:
            attrs.append(f'class="{cls}"')
        if size is not None:
            attrs.append(f'font-size="{size}"')
        if weight is not None:
            attrs.append(f'font-weight="{weight}"')
        if fill is not None:
            attrs.append(f'fill="{fill}"')
        if rotate is not None:
            attrs.append(f'transform="rotate({rotate:.1f} {x:.1f} {y:.1f})"')
        self.add(f"<text {' '.join(attrs)}>{html.escape(content)}</text>")

    def multiline_text(
        self,
        x,
        y,
        lines,
        *,
        cls="",
        anchor="middle",
        line_height=21,
        size=None,
        weight=None,
        fill=None,
    ):
        attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'text-anchor="{anchor}"']
        if cls:
            attrs.append(f'class="{cls}"')
        if size is not None:
            attrs.append(f'font-size="{size}"')
        if weight is not None:
            attrs.append(f'font-weight="{weight}"')
        if fill is not None:
            attrs.append(f'fill="{fill}"')
        tspans = []
        for i, line in enumerate(lines):
            dy = 0 if i == 0 else line_height
            tspans.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{html.escape(line)}</tspan>')
        self.add(f"<text {' '.join(attrs)}>{''.join(tspans)}</text>")

    def circle(self, cx, cy, r, fill, stroke="none", sw=1):
        self.add(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def line(self, x1, y1, x2, y2, stroke, sw=1):
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def rect(self, x, y, w, h, fill, rx=0):
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx:.1f}" fill="{fill}"/>'
        )

    def path(self, d, fill, stroke="#FFFFFF", sw=2):
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def finish(self):
        return "\n".join(self.parts + ["</svg>\n"])


def draw_donut(
    svg,
    cx,
    cy,
    values,
    r_outer,
    r_inner,
    *,
    start_angle=-90,
    labels=True,
    label_radius=205,
):
    total = sum(v for _, v, _ in values)
    angle = start_angle
    for label, value, color in values:
        sweep = value / total * 360
        start = angle
        end = angle + sweep
        svg.path(donut_path(cx, cy, r_outer, r_inner, start, end), color)

        if labels:
            mid = (start + end) / 2
            x0, y0 = polar(cx, cy, r_outer + 3, mid)
            x1, y1 = polar(cx, cy, r_outer + 21, mid)
            xt, yt = polar(cx, cy, label_radius, mid)
            align = "start" if math.cos(math.radians(mid)) >= 0 else "end"
            xt += 8 if align == "start" else -8
            svg.line(x0, y0, x1, y1, "#AEB4C2", 1)
            svg.line(x1, y1, xt - (6 if align == "start" else -6), yt, "#AEB4C2", 1)
            svg.multiline_text(
                xt,
                yt - 14,
                [label, fmt_int(value), pct(value, total)],
                cls="small",
                anchor=align,
                line_height=18,
            )
        angle = end


def draw_panel_a(svg, stats):
    cx, cy = 310, 270
    total = stats["rows"]
    task_counts = stats["task_counts"]
    category_counts = stats["category_counts"]

    svg.text(cx, 58, "Question type distribution", cls="title")

    inner_values = [
        ("Preference", category_counts["preference"], COLORS["preference"]),
        ("Recognition", category_counts["recognition"], COLORS["recognition"]),
    ]
    outer_values = [
        (TASK_LABELS[k], task_counts[k], COLORS[k])
        for k in TASK_ORDER
    ]

    draw_donut(svg, cx, cy, outer_values, 175, 121, labels=True, label_radius=228)
    draw_donut(svg, cx, cy, inner_values, 112, 72, labels=False)

    svg.circle(cx, cy, 68, "#FFFFFF")
    svg.multiline_text(cx, cy - 15, [fmt_int(total), "QA pairs"], cls="label", line_height=25, weight="700")

    legend_x, legend_y = cx - 90, cy + 218
    for i, (label, _, color) in enumerate(inner_values):
        x = legend_x + i * 165
        svg.rect(x, legend_y, 18, 18, color, 2)
        svg.text(x + 28, legend_y + 15, label, cls="small", anchor="start")


def draw_panel_b(svg, stats):
    cx, cy = 890, 270
    identity_counts = stats["identity_counts"]
    total = stats["total_identities"]

    svg.text(cx, 58, "Identity composition", cls="title")

    values = [
        (ATTRIBUTE_LABELS[k], identity_counts.get(k, 0), COLORS[k])
        for k in ATTRIBUTE_ORDER
    ]
    draw_donut(svg, cx, cy, values, 154, 90, labels=True, label_radius=215)

    svg.circle(cx, cy, 84, "#FFFFFF")
    svg.multiline_text(
        cx,
        cy - 25,
        [fmt_int(total), "identities", f"{identity_counts.get('human', 0)} human users"],
        cls="label",
        line_height=24,
        weight="700",
    )

    y = cy + 218
    x = cx - 196
    for i, key in enumerate(ATTRIBUTE_ORDER):
        lx = x + (i % 2) * 205
        ly = y + (i // 2) * 30
        svg.rect(lx, ly, 18, 18, COLORS[key], 2)
        svg.text(lx + 28, ly + 15, ATTRIBUTE_LABELS[key], cls="small", anchor="start")


def draw_panel_c(svg, stats):
    chart_x, chart_y = 1190, 105
    chart_w, chart_h = 610, 330
    split_task = stats["split_task_counts"]
    order = ["preference_mcq", "preference_yesno", "recognition_mcq", "recognition_yesno"]
    ymax = 6000

    svg.text(chart_x + chart_w / 2, 58, "Train/test samples by type", cls="title")

    # Grid and y-axis labels.
    for tick in [0, 2000, 4000, 6000]:
        y = chart_y + chart_h - tick / ymax * chart_h
        svg.line(chart_x, y, chart_x + chart_w, y, COLORS["grid"], 1)
        svg.text(chart_x - 15, y + 6, fmt_int(tick), cls="small", anchor="end")

    svg.line(chart_x, chart_y, chart_x, chart_y + chart_h, COLORS["ink"], 1.5)
    svg.line(chart_x, chart_y + chart_h, chart_x + chart_w, chart_y + chart_h, COLORS["ink"], 1.5)
    svg.text(chart_x - 68, chart_y + chart_h / 2, "Samples", cls="label", rotate=-90)

    bar_w = 42
    group_gap = chart_w / len(order)
    for i, task in enumerate(order):
        center = chart_x + group_gap * (i + 0.5)
        train = split_task[("train", task)]
        test = split_task[("test", task)]
        for j, (split, value, color) in enumerate(
            [("train", train, COLORS["train"]), ("test", test, COLORS["test"])]
        ):
            x = center - bar_w - 6 if j == 0 else center + 6
            h = value / ymax * chart_h
            y = chart_y + chart_h - h
            svg.rect(x, y, bar_w, h, color, 0)
            svg.text(x + bar_w / 2, y - 9, fmt_int(value), cls="tiny")

        svg.multiline_text(
            center,
            chart_y + chart_h + 31,
            TASK_SHORT_LABELS[task].split("\n"),
            cls="small",
            line_height=18,
        )

    # Legend.
    lx, ly = chart_x + chart_w - 185, chart_y - 43
    svg.rect(lx, ly, 20, 16, COLORS["train"], 2)
    svg.text(lx + 30, ly + 13, "Train", cls="small", anchor="start")
    svg.rect(lx + 94, ly, 20, 16, COLORS["test"], 2)
    svg.text(lx + 124, ly + 13, "Test", cls="small", anchor="start")


def build_svg(stats):
    svg = Svg(1880, 640)
    draw_panel_a(svg, stats)
    draw_panel_b(svg, stats)
    draw_panel_c(svg, stats)

    svg.text(310, 590, "(a) Distribution of question types in MMPB-Clean.", cls="caption")
    svg.text(890, 590, "(b) Distribution of identity categories.", cls="caption")
    svg.text(1495, 590, "(c) Train/test split by question type.", cls="caption")
    return svg.finish()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    dataset_path = (script_dir / args.dataset).resolve() if not args.dataset.is_absolute() else args.dataset
    output_path = (script_dir / args.output).resolve() if not args.output.is_absolute() else args.output

    stats = load_stats(dataset_path)
    svg = build_svg(stats)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")

    print(f"Wrote {output_path}")
    print(f"Rows: {stats['rows']:,}")
    print(f"Identities: {stats['total_identities']:,}")
    for task in TASK_ORDER:
        print(f"{task}: {stats['task_counts'][task]:,}")


if __name__ == "__main__":
    main()
