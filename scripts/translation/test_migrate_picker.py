import json
import tempfile
import unittest
from pathlib import Path

import migrate_picker as mp

LIB = "skills/code-animation-prompts/assets/library"
HTML = """<!doctype html>
<title>t</title>
<script id="data" type="application/json">{blob}</script>
<script>var x = 1;</script>
"""

MD = {
    "M1_white.md": """# M1 Whiteboard

- Category: M Motion Styles · Explainers
- Looks like: A hand draws on white.
- Best for: explaining concepts

## Style prompt

> This prompt is a rewritten, detailed version: all rules are fixed. What goes inside {{ }} is for you to fill in.

You are a motion engineer.

## Content

- Topic: {{topic}}

## Notes

### Reference

[Demo](https://example.com/a), ElevenLabs voiceover
""",
    "A1_rain.md": """# A1 Word Rain

- Category: A–G Code Samples · A Text
- Looks like: Words fall like rain.
- Best for: repetition, pressure
- Keywords: word rain, falling, pile-up

## Style prompt

Body that was never shown in the picker.
""",
    "O1_wings.md": """# O1 Wings

- Category: O 98 Best Picture Winners · Silent 1927–1938
- Looks like: A dogfight.
- Style: silent 3D · amber tint
- Keywords: 3D·B&W
- Year: 1927/28

## Style prompt

Smooth-shaded 3D. Restored instruction kept from the Chinese version.

## Notes

### Technique keywords

three.js 3D, amber tint

### Director's notes

Clawd plays a pilot.

### Reference source

William Wellman, 1927, Harry Perry
""",
    "M14_untitled.md": "# M14 \n\n- Category: M Motion Styles · Other Special Styles\n\n## Style prompt\n\n\n",
    "L1_news.md": """# L1 Caption News

- Category: L Lemo-Opuscar · Editing
- Looks like: News with the sound off.
- Best for: vertical versions

## Style prompt

# Caption News

## Notes

### Demo film

The Bee Ledger
""",
    "X1_hand.md": "# X1 Hand-drawn\n\n- Category: X code-video · code-video\n- Best for: explainers\n\n## Style prompt\n\nWarm paper.\n",
}


def entries():
    return [
        dict(id="M1", s="M", cat="讲解类", name="白板", desc="白底", fit="讲概念", prompt="你是一位工程师", img="",
             extra=[dict(h="参考", t="[样片](https://example.com/a)")], file="M1_white.md"),
        dict(id="A1", s="AG", cat="A 字", name="字雨", desc="落下", fit="压力", img="a.jpg",
             tags=["字雨", "落下", "堆积"], file="A1_rain.md"),
        dict(id="O1", s="O", cat="默片 1927–1938", name="翼", en="Wings", desc="空战", fit="默片", prompt="平滑着色",
             prompt_en="Older English without the restored instruction.", year="1927/28", tags=["3D·B&W"], img="",
             extra=[dict(h="技法关键词", t=["three.js 三维", "琥珀染色"]), dict(h="导演说明", t="扮飞行员"),
                    dict(h="参考出处", t=["William Wellman, 1927", "Harry Perry"])], file="O1_wings.md"),
        dict(id="M14", s="M", cat="其他特别的风格", name="", img="", file="M14_untitled.md"),
        dict(id="L1", s="L", cat="剪辑", name="字幕新闻", en="Caption News", desc="静音新闻", fit="竖屏", img="",
             desc_en="A news short that works with the sound off.", extra=[dict(h="示范片", t="The Bee Ledger")],
             file="L1_news.md"),
        dict(id="X1", s="X", cat="code-video", name="手绘", en="Hand-drawn", desc_en="Warm paper.", fit="讲解", img="",
             file="X1_hand.md"),
    ]


GLOSSARY = {
    "styles": {"M1": "Whiteboard", "A1": "Word Rain", "O1": "Wings", "M14": "Untitled", "L1": "Caption News",
               "X1": "Hand-drawn"},
    "labels": {"参考": "Reference", "技法关键词": "Technique keywords", "导演说明": "Director's notes",
               "参考出处": "Reference source", "示范片": "Demo film"},
}


def blob():
    return {"meta": [dict(id="M", label="M 动态风格", grp="ours", note="怎么动。")], "skills": [], "entries": entries()}


class Fixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.lib = Path(tmp.name)
        for name, text in MD.items():
            (self.lib / name).write_text(text, encoding="utf-8")

    def migrate(self, data=None, translations=None, keep=None):
        return mp.migrate(data or blob(), self.lib, GLOSSARY, translations=translations, keep=keep)

    def entry(self, data, entry_id):
        return next(e for e in data["entries"] if e["id"] == entry_id)


class EntryWithPrompt(Fixture):
    def test_prompt_is_the_english_section_without_the_rewrite_note_or_notes(self):
        m1 = self.entry(self.migrate()[0], "M1")
        self.assertEqual(m1["prompt"], "You are a motion engineer.\n\n## Content\n\n- Topic: {{topic}}")
        self.assertIn(m1["prompt"], MD["M1_white.md"])

    def test_metadata_comes_from_the_md(self):
        m1 = self.entry(self.migrate()[0], "M1")
        self.assertEqual((m1["name"], m1["cat"], m1["desc"], m1["fit"]),
                         ("Whiteboard", "Explainers", "A hand draws on white.", "explaining concepts"))

    def test_string_extra_comes_from_notes_with_translated_heading(self):
        m1 = self.entry(self.migrate()[0], "M1")
        self.assertEqual(m1["extra"], [{"h": "Reference", "t": "[Demo](https://example.com/a), ElevenLabs voiceover"}])

    def test_chinese_prompt_is_refused(self):
        (self.lib / "M1_white.md").write_text(MD["M1_white.md"].replace("motion engineer", "动效工程师"), encoding="utf-8")
        with self.assertRaisesRegex(mp.MigrationError, "M1.*prompt"):
            self.migrate()

    def test_keep_literals_are_allowed(self):
        (self.lib / "M1_white.md").write_text(MD["M1_white.md"].replace("motion engineer", "囍 engineer"), encoding="utf-8")
        data, _ = self.migrate(keep={"M1_white.md": ["囍"]})
        self.assertIn("囍", self.entry(data, "M1")["prompt"])


class EntryWithoutPrompt(Fixture):
    def test_no_prompt_is_added(self):
        a1 = self.entry(self.migrate()[0], "A1")
        self.assertNotIn("prompt", a1)
        self.assertEqual(a1["desc"], "Words fall like rain.")

    def test_tags_come_from_keywords(self):
        self.assertEqual(self.entry(self.migrate()[0], "A1")["tags"], ["word rain", "falling", "pile-up"])

    def test_asset_fields_and_series_are_untouched(self):
        a1 = self.entry(self.migrate()[0], "A1")
        self.assertEqual((a1["s"], a1["img"], a1["file"]), ("AG", "a.jpg", "A1_rain.md"))


class OEntry(Fixture):
    def test_one_english_prompt_with_restored_instructions(self):
        o1 = self.entry(self.migrate()[0], "O1")
        self.assertEqual(o1["prompt"], "Smooth-shaded 3D. Restored instruction kept from the Chinese version.")
        self.assertNotIn("prompt_en", o1)

    def test_redundant_en_is_dropped_and_year_kept(self):
        o1 = self.entry(self.migrate()[0], "O1")
        self.assertNotIn("en", o1)
        self.assertEqual((o1["name"], o1["year"], o1["fit"]), ("Wings", "1927/28", "silent 3D · amber tint"))

    def test_en_that_disagrees_with_the_glossary_is_dropped_for_the_glossary_name(self):
        data = blob()
        self.entry(data, "O1")["en"] = "Older Title"
        o1 = self.entry(self.migrate(data)[0], "O1")
        self.assertEqual(o1["name"], "Wings")
        self.assertNotIn("en", o1)

    def test_extras_keep_their_shape(self):
        extra = self.entry(self.migrate()[0], "O1")["extra"]
        self.assertEqual([x["h"] for x in extra], ["Technique keywords", "Director's notes", "Reference source"])
        self.assertEqual(extra[1]["t"], "Clawd plays a pilot.")
        self.assertEqual(extra[2]["t"], ["William Wellman, 1927", "Harry Perry"])


class Stub(Fixture):
    def test_stub_has_glossary_name_mapped_category_and_no_prompt(self):
        m14 = self.entry(self.migrate()[0], "M14")
        self.assertEqual((m14["name"], m14["cat"]), ("Untitled", "Other Special Styles"))
        for field in ["prompt", "desc", "fit", "tags"]:
            self.assertFalse(m14.get(field))

    def test_empty_prompt_stays_empty(self):
        data = blob()
        self.entry(data, "M14")["prompt"] = ""
        self.assertEqual(self.entry(self.migrate(data)[0], "M14")["prompt"], "")


class TodoList(Fixture):
    def setUp(self):
        super().setUp()
        self.todo = {item["key"]: item for item in self.migrate()[1]}

    def test_fields_without_md_source_are_listed(self):
        self.assertEqual(set(self.todo), {"meta.M.label", "meta.M.note", "O1.extra.0.t", "L1.desc_en", "X1.desc_en"})

    def test_items_carry_source_and_md_hint(self):
        self.assertEqual(self.todo["O1.extra.0.t"]["source"], ["three.js 三维", "琥珀染色"])
        self.assertEqual(self.todo["O1.extra.0.t"]["md"], "three.js 3D, amber tint")

    def test_list_without_chinese_is_not_listed(self):
        self.assertNotIn("O1.extra.2.t", self.todo)

    def test_tags_absent_from_md_are_listed(self):
        (self.lib / "A1_rain.md").write_text(MD["A1_rain.md"].replace("- Keywords: word rain, falling, pile-up\n", ""),
                                             encoding="utf-8")
        todo = {item["key"]: item for item in self.migrate()[1]}
        self.assertEqual(todo["A1.tags"]["source"], ["字雨", "落下", "堆积"])

    def test_tag_count_mismatch_is_listed_not_guessed(self):
        (self.lib / "A1_rain.md").write_text(MD["A1_rain.md"].replace("word rain, falling, pile-up", "word rain"),
                                             encoding="utf-8")
        self.assertIn("A1.tags", {item["key"] for item in self.migrate()[1]})

    def test_extra_with_chinese_and_no_md_section_is_listed(self):
        (self.lib / "L1_news.md").write_text(MD["L1_news.md"].split("## Notes")[0], encoding="utf-8")
        data = blob()
        self.entry(data, "L1")["extra"][0]["t"] = "蜜蜂账本"
        self.assertIn("L1.extra.0.t", {item["key"] for item in self.migrate(data)[1]})


class Translations(Fixture):
    TRANSLATIONS = {"meta.M.label": "M Motion Styles", "meta.M.note": "How it moves.",
                    "O1.extra.0.t": ["three.js 3D", "amber tint"],
                    "L1.desc_en": None, "X1.desc": "Warm paper.", "X1.desc_en": None}

    def test_todo_empties_and_values_apply(self):
        data, todo = self.migrate(translations=self.TRANSLATIONS)
        self.assertEqual(todo, [])
        self.assertEqual(data["meta"][0]["label"], "M Motion Styles")
        self.assertEqual(self.entry(data, "O1")["extra"][0]["t"], ["three.js 3D", "amber tint"])
        self.assertNotIn("desc_en", self.entry(data, "L1"))
        self.assertEqual(self.entry(data, "L1")["desc"], "News with the sound off.")
        self.assertEqual(self.entry(data, "X1")["desc"], "Warm paper.")

    def test_rerun_is_identical(self):
        first, _ = self.migrate(translations=self.TRANSLATIONS)
        again, todo = self.migrate(json.loads(json.dumps(first)), translations=self.TRANSLATIONS)
        self.assertEqual(first, again)
        self.assertEqual(todo, [])

    def test_translation_with_chinese_is_refused(self):
        with self.assertRaisesRegex(mp.MigrationError, "O1.extra.0.t"):
            self.migrate(translations={"O1.extra.0.t": ["三维", "amber"]})

    def test_unknown_translation_key_is_refused(self):
        with self.assertRaisesRegex(mp.MigrationError, "Z9"):
            self.migrate(translations={"Z9.desc": "x"})


class FailsLoudly(Fixture):
    def test_entry_missing_from_glossary(self):
        data = blob()
        data["entries"].append(dict(id="Q1", s="M", cat="x", name="y", img="", file="M14_untitled.md"))
        with self.assertRaisesRegex(mp.MigrationError, "Q1"):
            self.migrate(data)

    def test_missing_md(self):
        (self.lib / "A1_rain.md").unlink()
        with self.assertRaisesRegex(mp.MigrationError, "A1"):
            self.migrate()

    def test_heading_for_another_entry(self):
        (self.lib / "A1_rain.md").write_text(MD["A1_rain.md"].replace("# A1", "# A2"), encoding="utf-8")
        with self.assertRaisesRegex(mp.MigrationError, "A1.*heading"):
            self.migrate()

    def test_missing_category_line(self):
        (self.lib / "A1_rain.md").write_text(MD["A1_rain.md"].replace("- Category: A–G Code Samples · A Text\n", ""),
                                             encoding="utf-8")
        with self.assertRaisesRegex(mp.MigrationError, "A1.*Category"):
            self.migrate()

    def test_prompt_entry_with_empty_section(self):
        (self.lib / "O1_wings.md").write_text(MD["O1_wings.md"].replace(
            "Smooth-shaded 3D. Restored instruction kept from the Chinese version.\n", ""), encoding="utf-8")
        with self.assertRaisesRegex(mp.MigrationError, "O1.*prompt"):
            self.migrate()

    def test_unknown_extra_heading(self):
        data = blob()
        self.entry(data, "M1")["extra"][0]["h"] = "未知"
        with self.assertRaisesRegex(mp.MigrationError, "M1.*未知"):
            self.migrate(data)


class Grouping(Fixture):
    def test_categories_that_were_one_group_stay_one_group(self):
        data = blob()
        data["entries"].append(dict(id="M14b", s="M", cat="讲解类", name="", img="", file="M14_untitled.md"))
        with self.assertRaisesRegex(mp.MigrationError, "group"):
            mp.check_groups(data["entries"], [dict(e, cat="Explainers" if e["id"] == "M1" else e["id"]) for e in data["entries"]])

    def test_categories_that_were_separate_stay_separate(self):
        old = [dict(id="a", s="M", cat="甲"), dict(id="b", s="M", cat="乙")]
        new = [dict(id="a", s="M", cat="Same"), dict(id="b", s="M", cat="Same")]
        with self.assertRaisesRegex(mp.MigrationError, "group"):
            mp.check_groups(old, new)

    def test_same_label_in_two_series_is_fine(self):
        old = [dict(id="a", s="M", cat="甲"), dict(id="b", s="K", cat="乙")]
        new = [dict(id="a", s="M", cat="Same"), dict(id="b", s="K", cat="Same")]
        mp.check_groups(old, new)


class Files(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.lib = self.root / LIB
        self.lib.mkdir(parents=True)
        for name, text in MD.items():
            (self.lib / name).write_text(text, encoding="utf-8")
        (self.root / "docs/translation").mkdir(parents=True)
        (self.root / "docs/translation/glossary.json").write_text(json.dumps(GLOSSARY), encoding="utf-8")
        data = json.dumps(blob(), ensure_ascii=False, separators=(",", ":"))
        (self.lib / "style-picker.html").write_text(HTML.format(blob=data), encoding="utf-8")
        self.todo = self.root / ".build/translation/picker-todo.json"

    def picker(self):
        return (self.lib / "style-picker.html").read_text(encoding="utf-8")

    def test_run_writes_blob_and_todo_and_keeps_the_rest_of_the_html(self):
        mp.run(self.root)
        html = self.picker()
        self.assertIn("<script>var x = 1;</script>", html)
        self.assertNotIn("Older English", html)
        self.assertEqual(json.loads(self.todo.read_text(encoding="utf-8"))["count"], 5)

    def test_second_run_is_byte_identical(self):
        mp.run(self.root)
        html, todo = self.picker(), self.todo.read_text(encoding="utf-8")
        mp.run(self.root)
        self.assertEqual((self.picker(), self.todo.read_text(encoding="utf-8")), (html, todo))

    def test_translations_file_is_applied(self):
        self.todo.parent.mkdir(parents=True)
        (self.todo.parent / "picker-translations.json").write_text(json.dumps(Translations.TRANSLATIONS), encoding="utf-8")
        mp.run(self.root)
        self.assertEqual(json.loads(self.todo.read_text(encoding="utf-8"))["count"], 0)

    def test_script_closing_text_in_a_prompt_cannot_end_the_data_block(self):
        md = self.lib / "M1_white.md"
        md.write_text(md.read_text(encoding="utf-8").replace("motion engineer.", "motion engineer. </script><!-- x"),
                      encoding="utf-8")
        mp.run(self.root)
        data = mp.parse_blob(self.picker())
        self.assertIn("</script><!-- x", next(e for e in data["entries"] if e["id"] == "M1")["prompt"])

    def test_page_without_data_block_fails(self):
        (self.lib / "style-picker.html").write_text("<html></html>", encoding="utf-8")
        with self.assertRaises(mp.MigrationError):
            mp.run(self.root)


if __name__ == "__main__":
    unittest.main()
