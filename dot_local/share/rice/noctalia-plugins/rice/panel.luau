--!nonstrict
-- Thumbnail grid backed by `rice list --json`. Choosing a wallpaper runs
-- `rice select`: an approved palette applies; an unknown image is only drafted,
-- and the panel offers its report, a reversible preview, or approval.

local COLUMNS = 3
local THUMB_W, THUMB_H = 272, 153

local items = {}
local message = "Loading wallpapers…"
local pending = nil -- wallpaper whose draft awaits review
local busy = false

local function rice(args, onDone)
  -- Positional arguments keep paths with spaces intact; $HOME finds rice outside PATH.
  local argv = { "sh", "-c", '"$HOME/.local/bin/rice" "$@"', "rice" }
  for _, arg in ipairs(args) do
    table.insert(argv, arg)
  end
  busy = true
  noctalia.runAsync(argv, function(result)
    busy = false
    onDone(result)
  end, 60000)
end

local function lastLine(text)
  local line = ""
  for part in string.gmatch(text or "", "[^\n]+") do
    line = part
  end
  return line
end

local render

local function refresh()
  rice({ "list", "--json", "--thumbnails" }, function(result)
    if result.exitCode ~= 0 then
      message = "rice list failed: " .. lastLine(result.stderr)
    else
      local data, err = noctalia.json.decode(result.stdout)
      items = data and data.wallpapers or {}
      if pending then
        for _, item in ipairs(items) do
          if item.path == pending.path then pending = item; break end
        end
      end
      if err then message = "Could not read rice output: " .. err
      elseif message == "Loading wallpapers…" then message = "Choose a wallpaper; new images open a draft for review." end
    end
    render()
  end)
end

local function select(item)
  if busy then
    return
  end
  message = "Applying " .. item.name .. "…"
  render()
  rice({ "select", item.path }, function(result)
    if result.exitCode == 0 then
      pending = nil
      message = "Applied " .. item.name
    elseif result.exitCode == 3 then
      pending = item
      message = "Draft ready. Review the colors or preview them before approving."
    else
      message = "rice: " .. lastLine(result.stderr)
      noctalia.notifyError("rice", message)
    end
    refresh()
  end)
end

local function action(args, done)
  return function()
    if busy then
      return
    end
    rice(args, function(result)
      message = result.exitCode == 0 and done or ("rice: " .. lastLine(result.stderr))
      if result.exitCode == 0 and args[1] ~= "preview" then
        pending = nil
      end
      refresh()
    end)
  end
end

local function card(item)
  local badge = item.status == "approved" and "primary" or "on_surface_variant"
  return ui.column({ gap = 6, width = THUMB_W, height = 186, justify = "start" }, {
    item.thumbnail and ui.image({
      path = item.thumbnail,
      width = THUMB_W,
      height = THUMB_H,
      fit = "cover",
      radius = 10,
      border = item.current and "primary" or nil,
      borderWidth = item.current and 2 or 0,
      tooltip = item.path,
      onClick = function()
        select(item)
      end,
    }) or ui.button({ text = item.name, height = THUMB_H, onClick = function()
      select(item)
    end }),
    ui.row({ gap = 8, align = "center" }, {
      ui.label({ text = item.name, color = "on_surface", flexGrow = 1 }),
      ui.label({ text = item.status, color = badge }),
    }),
  })
end

local function review()
  if not pending then
    return ui.spacer({ height = 0 })
  end
  local path, report = pending.path, pending.report or ""
  return ui.row({ gap = 8, align = "center", padding = 8, radius = 10, fill = "surface_container" }, {
    ui.label({ text = pending.name .. " needs approval", color = "on_surface", flexGrow = 1 }),
    ui.button({ text = "Report", variant = "outline", onClick = function()
      if report ~= "" then noctalia.runAsync({ "xdg-open", report }) end
    end }),
    ui.button({ text = "Preview", variant = "secondary", onClick = action({ "preview", path }, "Previewing draft; Restore undoes it") }),
    ui.button({ text = "Approve", variant = "primary", onClick = action({ "approve", path, "--apply" }, "Approved and applied") }),
  })
end

render = function()
  local rows = {}
  for i = 1, #items, COLUMNS do
    local row = {}
    for j = i, math.min(i + COLUMNS - 1, #items) do
      table.insert(row, card(items[j]))
    end
    table.insert(rows, ui.row({ gap = 12, height = 192, align = "start", justify = "start" }, row))
  end
  panel.render(ui.column({ gap = 12, align = "stretch", justify = "start" }, {
    ui.row({ gap = 8, align = "center" }, {
      ui.label({ text = "Wallpapers", fontSize = 16, fontWeight = "bold", color = "on_surface", flexGrow = 1 }),
      ui.button({ text = "Fonts", variant = "ghost", onClick = function()
        panel.close()
        noctalia.runAsync({ "sh", "-c", '"$HOME/.local/bin/rice" fonts --pick' })
      end }),
      ui.button({ text = "Restore previous", variant = "ghost", onClick = action({ "restore" }, "Previous setup restored") }),
      ui.button({ glyph = "close", variant = "ghost", onClick = function()
        panel.close()
      end }),
    }),
    ui.label({ text = message, color = "on_surface_variant" }),
    review(),
    ui.scroll({ height = math.max(192, math.min(480, math.ceil(#items / COLUMNS) * 204)), gap = 12, justify = "start" }, rows),
  }))
end

function onOpen(_context)
  render()
  refresh()
end
