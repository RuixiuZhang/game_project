def handle_trigger_event(event, world_state):
    if not event:
        return

    event_type = event.get("type")

    if event_type == "battle":
        print("⚔ 触发战斗：", event)
        world_state["mode"] = "battle"

    elif event_type == "unlock_story":
        story_id = event.get("story_id")
        print("📖 解锁剧情：", story_id)
        world_state["stories"].add(story_id)

    elif event_type == "propose_new_story":
        print("✨ AI 提议新剧情：")
        print(event)

    else:
        print("⚠ 未识别的 trigger_event：", event)