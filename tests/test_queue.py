import re

QUEUE_JSON = """
{
  "_class" : "hudson.model.Queue",
  "discoverableItems" : [

  ],
  "items" : [
    {
      "_class" : "hudson.model.Queue$BlockedItem",
      "actions" : [
        {
          "_class" : "hudson.model.CauseAction",
          "causes" : [
            {
              "_class" : "hudson.model.Cause$UserIdCause",
              "shortDescription" : "Started by user admin",
              "userId" : "admin",
              "userName" : "admin"
            }
          ]
        }
      ],
      "blocked" : true,
      "buildable" : false,
      "id" : 14,
      "inQueueSince" : 1662756642196,
      "params" : "",
      "stuck" : false,
      "task" : {
        "_class" : "hudson.model.FreeStyleProject",
        "name" : "test",
        "url" : "http://localhost:8080/job/test/",
        "color" : "blue_anime"
      },
      "url" : "queue/item/14/",
      "why" : "Build #8 is already in progress (ETA: 1 min 33 sec)",
      "buildableStartMilliseconds" : 1662756642197
    }
  ]
}
"""

QUEUE_ITEM_JSON = """
{
  "_class" : "hudson.model.Queue$BlockedItem",
  "actions" : [
    {
      "_class" : "hudson.model.CauseAction",
      "causes" : [
        {
          "_class" : "hudson.model.Cause$UserIdCause",
          "shortDescription" : "Started by user admin",
          "userId" : "admin",
          "userName" : "admin"
        }
      ]
    }
  ],
  "blocked" : true,
  "buildable" : false,
  "id" : 16,
  "inQueueSince" : 1662762046812,
  "params" : "",
  "stuck" : false,
  "task" : {
    "_class" : "hudson.model.FreeStyleProject",
    "name" : "test",
    "url" : "http://localhost:8080/job/test/",
    "color" : "blue_anime"
  },
  "url" : "queue/item/16/",
  "why" : "Build #10 is already in progress (ETA: 1 min 3 sec)",
  "buildableStartMilliseconds" : 1662762046816
}
"""


async def test_get(jenkins, aiohttp_mock):
    aiohttp_mock.get(
        re.compile(r'.+/queue/api/json'),
        content_type='application/json;charset=utf-8',
        body=QUEUE_JSON
    )

    jenkins.crumb = False
    queue = await jenkins.queue.get_all()
    assert len(queue) == 1


async def test_get_info(jenkins, aiohttp_mock):
    aiohttp_mock.get(
        re.compile(r'.+/queue/item/\d+/api/json'),
        content_type='application/json;charset=utf-8',
        body=QUEUE_ITEM_JSON
    )

    jenkins.crumb = False
    item = await jenkins.queue.get_info(16)
    assert item['stuck'] is False


async def test_cancel(jenkins, aiohttp_mock):
    aiohttp_mock.post(
        re.compile(r'.+/queue/cancelItem'),
    )

    jenkins.crumb = False
    assert await jenkins.queue.cancel(16) is None
