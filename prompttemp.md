[Task]
Провести рефактор механики экипировки предметов по плану.

[Plan]
@core/systems/inventory_system.py

Добавить метод `unequip` после `_equip`:

```python
def unequip(self, slot: str, player: dict) -> dict:
    source_key = f"equipped_{slot}"
    source = self.get_container(source_key)
    item_key_name, = source

    self._increment_item_count(player["inventory"], item_key_name, 1)
    source.clear()

    log = LOG["inventory_log_template"].copy()
    log["action"] = "unequip"
    log["item_key_name"] = item_key_name
    log["source"] = source_key
    log["slot"] = slot
    return log
```

---

@core/engine.py

Удалить `inventory_equip` целиком — она идентична `inventory_use`.

Добавить `inventory_unequip`:

```python
def inventory_unequip(slot: str, run_state: dict) -> dict:
    player = run_state["player"]
    state_wrapped = StateWrapper(run_state)
    inventory_system = InventorySystem(state_wrapped.get_container, run_state["inventory_state"])
    return inventory_system.unequip(slot, player)
```

---

@core/rogue_interface.py

В методе `inventory_equip_item` изменить вызов:

```diff
inventory_state["selected_item_source"] = source

- log = engine.inventory_equip(state)
+ log = engine.inventory_use(state)
return await self._finalize_game(user_id, state, log)

```

Добавить метод `inventory_unequip_item`:

```python
async def inventory_unequip_item(self, user_id: int, slot: str) -> Contract:
    state = await self.database.get_user_run_state(user_id)
    log = engine.inventory_unequip(slot, state)
    return await self._finalize_game(user_id, state, log)
```

В `process_action` заменить `case "move_item_to"` для unequip — добавить отдельный `case "unequip"`:

```diff
+ case "unequip":
+     slot = parsed.params["slot"]
+     return await rogue_interface.inventory_unequip_item(user_id, slot)
```

Добавить `"unequip": {"args": ["slot"]}` в `data/rules.json → command_schemas`.

---

@core/ui_builder.py

В `_inventory_select_buttons()` изменить кнопку unequip:

```diff
  if selected_item_source.startswith("equipped_"):
-     action_btn = Button(label=UI_LABELS["unequip"], action=f"move_item_to:inventory")
+     slot = selected_item_source.replace("equipped_", "")
+     action_btn = Button(label=UI_LABELS["unequip"], action=f"unequip:{slot}")
```

---

@data/rules.json

```diff
  "command_schemas": {
+     "unequip": {"args": ["slot"]},
      ...
  }
```
