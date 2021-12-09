def draw_table(columns, rows):
    if rows:
        if prepare_table_columns(columns, rows):
            for c in columns:
                if c["align"] == "left":
                    c["header-padded"] = c["header"] + (" " * (c["width"] - len(c["header"])))
                else:
                    c["header-padded"] = (" " * (c["width"] - len(c["header"]))) + c["header"]

            rows_padded = [{c["attr"]: row_get_attr(r, c) for c in columns} for r in rows]
            for r in rows_padded:
                for c in columns:
                    r[c["attr"]] = str(r[c["attr"]]) if r[c["attr"]] is not None else ""

                    if c["align"] == "left":
                        r[c["attr"]] = r[c["attr"]] + (" " * (c["width"] - len(r[c["attr"]])))
                    else:
                        r[c["attr"]] = (" " * (c["width"] - len(r[c["attr"]]))) + r[c["attr"]]

            tl = "\u250C"
            tr = "\u2510"
            bl = "\u2514"
            br = "\u2518"
            td = "\u252C"
            bd = "\u2534"
            ld = "\u251C"
            rd = "\u2524"
            vd = "\u2502"
            hd = "\u2500"
            cd = "\u253C"

            s = "```"
            s += f"{tl}{td.join([(c['width'] + 2) * hd for c in columns])}{tr}\n"
            s += f"{vd + ' '}{(' ' + vd + ' ').join([c['header-padded'] for c in columns])}{' ' + vd}\n"
            s += f"{ld}{cd.join([(c['width'] + 2) * hd for c in columns])}{rd}\n"

            for r in rows_padded:
                s += f"{vd + ' '}{(' ' + vd + ' ').join([r[c['attr']] for c in columns])}{' ' + vd}\n"

            s += f"{bl}{bd.join([(c['width'] + 2) * hd for c in columns])}{br}\n"
            s += "```"
        else:
            s = "Unable to represent this data as a table."
    else:
        s = "There's nothing to show."

    return s


def format_timespan(t):
    if t >= 3600:
        s = f"{t // 3600}h {(t % 3600) // 60:>2}m {t % 60:>2}s"
    elif t >= 60:
        s = f"{t // 60}m {t % 60:>2}s"
    else:
        s = f"{t}s"

    return s


async def format_user(bot, uid, mention=False):
    if uid:
        if mention:
            s = f"<@{uid}>"
        else:
            u = await get_user(bot, uid)

            if u:
                s = f"`{u}`"
            else:
                s = f"<u#{uid}>"
    else:
        s = ""

    return s


def get_channel(guild, channel_name, channel_type=""):
    if channel_type == "text":
        channels = guild.text_channels
    elif channel_type == "voice":
        channels = guild.voice_channels
    else:
        channels = guild.channels

    for c in channels:
        if c.name == channel_name:
            return c


async def get_user(bot, uid):
    u = None

    if uid:
        u = bot.get_user(uid)

        if not u:
            u = await bot.fetch_user(uid)

    return u


async def get_user_string(bot, uid):
    if uid:
        u = await get_user(bot, uid)

        if u:
            s = str(u)
        else:
            s = str(uid)
    else:
        s = ""

    return s


def parse_int_param(v, allow_negative=True, allow_zero=True):
    if v:
        if isinstance(v, str):
            if str.isnumeric(v) and v.find(".") == -1:
                v = int(v)

                if not allow_zero and v == 0:
                    v = None
                elif not allow_negative and v < 0:
                    v = None
            else:
                v = None
        elif not isinstance(v, int):
            v = None
    else:
        v = None

    return v


def prepare_table_columns(columns, rows):
    fail = False

    for c in columns:
        if not "attr" in c:
            fail = True
            break

        if not "header" in c:
            c["header"] = c["attr"]

        if not "align" in c or c["align"] not in ("left", "right"):
            c["align"] = "left"

        c["width"] = max(c.get("width", 0), len(c["header"]))

    if not fail:
        for r in rows:
            for c in columns:
                if row_has_attr(r, c):
                    c["width"] = max(c["width"], len(row_get_attr(r, c)))
                else:
                    fail = True
                    break

            if fail:
                break

    return not fail


def row_get_attr(row, col_def):
    x = row[col_def["attr"]] if isinstance(row, dict) else getattr(row, col_def["attr"])

    if "format" in col_def:
        x = col_def["format"](x)
    else:
        x = str(x) if x is not None else ""

    return x


def row_has_attr(row, col_def):
    return col_def["attr"] in row if isinstance(row, dict) else hasattr(row, col_def["attr"])
