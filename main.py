import flet as ft
import win32_core as core

def main(page: ft.Page):
    page.title = "信息报送转换"
    page.bgcolor = "#F5F7FA"
    page.padding = 12
    page.scroll = ft.ScrollMode.AUTO
    selected_tag = {"value": ""}

    input_ta = ft.TextField(
        label="原始内容", multiline=True, min_lines=4, max_lines=6,
        border_color="#D0D5DD", bgcolor="white", text_size=14,
    )

    tag_buttons = []
    tag_chips = []
    for cat, items in core.TAG_GROUPS:
        for seq, tag in items:
            btn = ft.Chip(
                label=ft.Text(tag, size=12),
                selected=False,
                bgcolor="#D6E4FF",
                selected_color="white",
                show_checkmark=False,
            )
            def on_tag(e, t=tag, s=seq):
                for b in tag_buttons:
                    b.selected = False
                e.control.selected = True
                selected_tag["value"] = t
                tag_input.value = t
                hint.value = "%s：%s" % (s, core.TAG_DESCRIPTIONS.get(s, ""))
                for b in tag_buttons:
                    b.update()
                tag_input.update()
                hint.update()
            btn.on_select = on_tag
            tag_buttons.append(btn)
            tag_chips.append(btn)

    hint = ft.Text("", color="#1a73e8", size=12)

    tag_input = ft.TextField(label="标签", bgcolor="white", border_color="#D0D5DD", text_size=14)
    time_input = ft.TextField(label="时间", bgcolor="white", border_color="#D0D5DD", text_size=14)
    city_input = ft.TextField(label="城市", bgcolor="white", border_color="#D0D5DD", text_size=14)
    plat_input = ft.TextField(label="平台", bgcolor="white", border_color="#D0D5DD", text_size=14)
    author_input = ft.TextField(label="作者", bgcolor="white", border_color="#D0D5DD", text_size=14)
    douyin_input = ft.TextField(label="抖音号", bgcolor="white", border_color="#D0D5DD", text_size=14)
    sum_input = ft.TextField(label="摘要", multiline=True, min_lines=2, max_lines=3,
                             bgcolor="white", border_color="#D0D5DD", text_size=14)
    url_input = ft.TextField(label="链接", bgcolor="white", border_color="#D0D5DD", text_size=14)

    def do_clip(e):
        input_ta.value = page.get_clipboard() or ""
        input_ta.update()

    def do_clear(e):
        for f in [input_ta, tag_input, time_input, city_input, plat_input,
                  author_input, douyin_input, sum_input, url_input]:
            f.value = ""
            f.update()
        hint.value = ""
        hint.update()

    def do_convert(e):
        txt = input_ta.value.strip() if input_ta.value else ""
        if not txt:
            return
        result, err = core.convert_text(txt)
        if err:
            page.open(ft.SnackBar(ft.Text(err)))
            return
        fields = core.parse_result_to_fields(result)
        if selected_tag["value"]:
            fields["tag"] = selected_tag["value"]
        tag_input.value = fields["tag"]
        time_input.value = fields["time"]
        city_input.value = fields["city"]
        plat_input.value = fields["platform"]
        author_input.value = fields["author"]
        douyin_input.value = fields["douyin_id"]
        sum_input.value = fields["summary"]
        url_input.value = fields["url"]
        for f in [tag_input, time_input, city_input, plat_input,
                  author_input, douyin_input, sum_input, url_input]:
            f.update()

    def do_copy(e):
        fields = {"tag": tag_input.value, "time": time_input.value,
                  "city": city_input.value, "platform": plat_input.value,
                  "author": author_input.value, "douyin_id": douyin_input.value,
                  "summary": sum_input.value, "url": url_input.value}
        result = core.build_result_from_fields(fields)
        page.set_clipboard(result)
        page.open(ft.SnackBar(ft.Text("已复制")))

    page.add(
        ft.Container(
            ft.Column([
                ft.Text("信息报送转换", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                input_ta,
                ft.Row([
                    ft.ElevatedButton("读取剪贴板", bgcolor="#E8EAED", color="black",
                                      height=44, expand=True, on_click=do_clip),
                    ft.ElevatedButton("清空", bgcolor="#D93025", color="white",
                                      height=44, expand=True, on_click=do_clear),
                ], spacing=8),
                ft.Divider(),
                ft.Text("分类标签", weight=ft.FontWeight.BOLD),
                ft.Wrap(spacing=6, run_spacing=6, controls=tag_chips),
                hint,
                ft.Divider(),
                ft.Text("报送内容", weight=ft.FontWeight.BOLD),
                tag_input,
                time_input,
                city_input,
                plat_input,
                author_input,
                douyin_input,
                sum_input,
                url_input,
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton("转换格式", bgcolor="#1664FF", color="white",
                                      height=48, expand=True, on_click=do_convert),
                    ft.ElevatedButton("复制结果", bgcolor="#34A853", color="white",
                                      height=48, expand=True, on_click=do_copy),
                ], spacing=8),
            ], spacing=10),
            padding=10,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
