import datetime as dt
import unittest

from mindsearch.news.aihot import (
    AINewsItem,
    format_daily_digest,
    parse_aihot_daily,
)


SAMPLE_HTML = """
<html>
  <head>
    <script id="__NEXT_DATA__" type="application/json">
      {
        "props": {
          "pageProps": {
            "dehydratedState": {
              "queries": [
                {
                  "state": {
                    "data": {
                      "items": [
                        {
                          "title": "OpenAI 发布全新研究模型",
                          "url": "https://example.com/openai",
                          "summary": "模型在推理任务上取得重大进展",
                          "source": {"name": "TechCrunch"},
                          "publishedAt": "2024-05-01T08:30:00Z"
                        },
                        {
                          "title": "DeepMind 公布多模态突破",
                          "url": "/news/deepmind",
                          "description": "新的多模态模型能够处理文本与图像。",
                          "publisher": "The Verge",
                          "date": "2024-05-01 07:00"
                        }
                      ]
                    }
                  }
                }
              ]
            }
          }
        }
      }
    </script>
  </head>
</html>
"""


class ParseAihotTests(unittest.TestCase):
    def test_parse_aihot_daily_from_next_data(self) -> None:
        items = parse_aihot_daily(SAMPLE_HTML)
        self.assertEqual(len(items), 2)
        first = items[0]
        self.assertIsInstance(first, AINewsItem)
        self.assertEqual(first.title, "OpenAI 发布全新研究模型")
        self.assertIn("TechCrunch", first.source)
        self.assertIsNotNone(first.published_at)
        second = items[1]
        self.assertEqual(second.url, "https://aihot.today/news/deepmind")
        self.assertIn("多模态", second.summary)

    def test_format_daily_digest(self) -> None:
        items = parse_aihot_daily(SAMPLE_HTML)
        digest = format_daily_digest(items, limit=1, report_date=dt.date(2024, 5, 1))
        self.assertIn("AI Hot 今日 AI 日报", digest)
        self.assertIn("OpenAI 发布全新研究模型", digest)
        self.assertIn("更多资讯", digest)
        self.assertIn("TechCrunch", digest)


if __name__ == "__main__":
    unittest.main()
