# -*- coding: utf-8 -*-
import unittest
import pykakasi

class TestPyKakasi(unittest.TestCase):

    def test_kakasi_hepburn(self):

        TESTS = [
            (u"",""),
            (u"構成",         "Kousei"),
            (u"好き",         "Suki"),
            (u"大きい",       "Ookii"),
            (u"かんたん",     "kantan"),
            (u"にゃ",         "nya"),
            (u"っき",         "kki"),
            (u"っふぁ",       "ffa"),
            (u"漢字とひらがな交じり文", "Kanji tohiragana Majiri Bun"),
            (u"Alphabet 123 and 漢字", "Alphabet 123 and Kanji"),
            (u"日経新聞", "Nikkeishinbun"),
            (u"日本国民は、","Nihonkokumin ha,")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H","a")
        kakasi.setMode("K","a")
        kakasi.setMode("J","a")
        kakasi.setMode("r","Hepburn")
        kakasi.setMode("s", True)
        kakasi.setMode("E", "a")
        kakasi.setMode("a", None)
        kakasi.setMode("C", True)
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_kunrei(self):

        TESTS = [
            (u"", ""),
            (u"構成",         "Kousei"),
            (u"好き",          "Suki"),
            (u"大きい",       "Ookii"),
            (u"かんたん",     "kantan"),
            (u"にゃ",          "nya"),
            (u"っき",           "kki"),
            (u"っふぁ",        "ffa"),
            (u"漢字とひらがな交じり文", "Kanzi tohiragana Maziri Bun"),
            (u"Alphabet 123 and 漢字", "Alphabet 123 and Kanzi"),
            (u"日経新聞",     "Nikkeisinbun"),
            (u"日本国民は、", "Nihonkokumin ha,")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H","a")
        kakasi.setMode("K","a")
        kakasi.setMode("J","a")
        kakasi.setMode("r","Kunrei")
        kakasi.setMode("E","a")
        kakasi.setMode("s", True)
        kakasi.setMode("a", None)
        kakasi.setMode("C", True)
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_J2H(self):

        TESTS = [
            (u"",""),
            (u"構成",         u"こうせい"),
            (u"好き",         u"すき"),
            (u"大きい",       u"おおきい"),
            (u"かんたん",     u"かんたん"),
            (u"にゃ",         u"にゃ"),
            (u"っき",         u"っき"),
            (u"っふぁ",       u"っふぁ"),
            (u"漢字とひらがな交じり文", u"かんじとひらがなまじりぶん"),
            (u"Alphabet 123 and 漢字", u"Alphabet 123 and かんじ"),
            (u"日経新聞",     u"にっけいしんぶん"),
            (u"日本国民は、", u"にほんこくみんは、"),
            (u"苦々しい",         u"にがにがしい")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H",None)
        kakasi.setMode("K",None)
        kakasi.setMode("J","H")
        kakasi.setMode("s",False)
        kakasi.setMode("C",True)
        kakasi.setMode("E",None)
        kakasi.setMode("a",None)
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_J2K(self):

        TESTS = [
            (u"",""),
            (u"構成",         u"コウセイ"),
            (u"好き",         u"スキ"),
            (u"大きい",       u"オオキイ"),
            (u"かんたん",     u"かんたん"),
            (u"漢字とひらがな交じり文", u"カンジとひらがなマジリブン"),
            (u"Alphabet 123 and 漢字", u"Alphabet 123 and カンジ")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H",None)
        kakasi.setMode("K",None)
        kakasi.setMode("J","K")
        kakasi.setMode("s",False)
        kakasi.setMode("C",True)
        kakasi.setMode("E",None)
        kakasi.setMode("a",None)
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)


    def test_kakasi_H2K(self):

        TESTS = [
            (u"",""),
            (u"かんたん",     u"カンタン"),
            (u"にゃ",         u"ニャ")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H","K")
        kakasi.setMode("S"," ")
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_K2H(self):

        TESTS = [
            (u"",""),
            (u"カンタン",u"かんたん"),
            (u"ニャ",    u"にゃ")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("K","H")
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)
 
    def test_wakati(self):
        TESTS = [
                (u"",u""),
                (u"交じり文", u"交じり 文"),
                (u"ひらがな交じり文", u"ひらがな 交じり 文"),
                (u"漢字とひらがな交じり文", u"漢字 とひらがな 交じり 文")
        ]
        wakati = pykakasi.wakati()
        converter = wakati.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_a2E(self):

        TESTS = [
            ("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
             u"ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"),
            ("abcdefghijklmnopqrstuvwxyz",
             u"ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"),
            ("!\"#$%&'()*+,-./_ {|}~",
             u"！＂＃＄％＆＇（）＊＋，－．／＿　｛｜｝～")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("a","E")
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_E2a(self):

        TESTS = [
            (u"ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            (u"ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
              "abcdefghijklmnopqrstuvwxyz"),
            (u"！＂＃＄％＆＇（）＊＋，－．／＿　｛｜｝～",
             "!\"#$%&'()*+,-./_ {|}~")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("E","a")
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_numbers(self):

        TESTS = [
            (u"１２３４５６７８９０",
              "1234567890"),
            (u"一 二 三 四 五 六 七 八 九 〇",
              "ichi ni san shi go roku shichi hachi kyuu (maru)")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("E","a")
        kakasi.setMode("J","a")
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_passport(self):

        TESTS = [
            (u"",""),
            (u"構成",         "Kosei"),
            (u"大野",         "Ono"),
            (u"斎藤",         "Saito"),
            (u"菅野",         "Kanno"),
            (u"本田",         "Honda"),
            (u"一式",         "Isshiki"),
            (u"別府",         "Beppu"),
            (u"ジェ",         "jie"),
            (u"チェ",         "chie"),
            (u"ティ",         "tei"),
            (u"ディ",         "dei"),
            (u"デュ",         "deyu"),
            (u"ファ",         "fua"),
            (u"フィ",         "fui"),
            (u"フェ",         "fue"),
            (u"フォ",         "fuo"),
            (u"ヴァ",         "bua"),
            (u"ヴィ",         "bui"),
            (u"ヴ",           "bu"),
            (u"ヴェ",         "bue"),
            (u"ヴォ",         "buo"),
            (u"じぇ",         "jie"),
            (u"ちぇ",         "chie"),
            (u"てぃ",         "tei"),
            (u"でぃ",         "dei"),
            (u"でゅ",         "deyu"),
            (u"ふぁ",         "fua"),
            (u"ふぃ",         "fui"),
            (u"ふぇ",         "fue"),
            (u"ふぉ",         "fuo")
         ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H","a")
        kakasi.setMode("K","a")
        kakasi.setMode("J","a")
        kakasi.setMode("r","Passport")
        kakasi.setMode("E","a")
        kakasi.setMode("C",True)
        kakasi.setMode("a",None)
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)


    @unittest.skip("Not yet implemented properly")
    def test_kakasi_passport_specialcase(self):

        TESTS = [
            (u"えっちゅう",   "etchu"),
            (u"はっちょう",   "hatcho"),
            (u"エッチュウ",   "etchu"),
            (u"ハッチョウ",   "hatcho")
         ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H","a")
        kakasi.setMode("K","a")
        kakasi.setMode("J","a")
        kakasi.setMode("r","Passport")
        kakasi.setMode("E","a")
        kakasi.setMode("a",None)
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)

    def test_kakasi_hepburn_nocapital(self):

        TESTS = [
            (u"",""),
            (u"構成",         "kousei"),
            (u"好き",         "suki"),
            (u"大きい",       "ookii"),
            (u"かんたん",     "kantan"),
            (u"にゃ",         "nya"),
            (u"っき",         "kki"),
            (u"っふぁ",       "ffa"),
            (u"漢字とひらがな交じり文", "kanji tohiragana majiri bun"),
            (u"Alphabet 123 and 漢字", "Alphabet 123 and kanji"),
            (u"日経新聞", "nikkeishinbun"),
            (u"日本国民は、","nihonkokumin ha,")
        ]

        kakasi = pykakasi.kakasi()
        kakasi.setMode("H","a")
        kakasi.setMode("K","a")
        kakasi.setMode("J","a")
        kakasi.setMode("r","Hepburn")
        kakasi.setMode("s", True)
        kakasi.setMode("E","a")
        kakasi.setMode("a", None)
        kakasi.setMode("C", False)
        converter  = kakasi.getConverter()
        for case, result in TESTS:
            self.assertEqual(converter.do(case), result)
