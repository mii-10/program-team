# -*- coding: utf-8 -*-

import discord
from discord import TextChannel, app_commands
from discord.ext import commands
import asyncio
import m10s_util as ut

from typing import Optional, Literal

import json


class settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="settings")
    @ut.runnable_check_for_appcmd()
    @ut.runnable_check()
    async def setting_cmds(self, ctx):pass

    @setting_cmds.command(description="prefixのユーザー設定")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.describe(mode="どうするか")
    @app_commands.describe(ipf="カスタムprefixの文字列")
    @app_commands.choices(mode=[
            app_commands.Choice(name="view", value=0),
            app_commands.Choice(name="set", value=1),
            app_commands.Choice(name="delete", value=2),
        ])
    async def userprefix(self, ctx, mode:int, ipf:Optional[str]=""):
        if ipf == "@everyone" or ipf == "@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        upf = await self.bot.cursor.fetchone(
            "select * from users where id=%s", (ctx.author.id,))
        prefixes = json.loads(upf["prefix"])
        #upf = await self.bot.cursor.fetchone()
        if mode == 0:
            await ctx.send(embed=ut.getEmbed("ユーザーのprefix", f'```{",".join(prefixes)}```'))
        elif mode == 1:
            spf = prefixes + [ipf]
            await self.bot.cursor.execute(
                "UPDATE users SET prefix = %s WHERE id = %s", (json.dumps(spf), ctx.author.id))
            await ctx.send(await ctx._("upf-add", ipf))
        elif mode == 2:
            prefixes.remove(ipf)
            await self.bot.cursor.execute(
                "UPDATE users SET prefix = %s WHERE id = %s", (json.dumps(prefixes), ctx.author.id))
            await ctx.send(f"prefixから{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択", "`view`または`set`または`del`を指定してください。"))

    @setting_cmds.command(description="prefixのサーバー設定")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(mode="どうするか")
    @app_commands.describe(ipf="カスタムprefixの文字列")
    @app_commands.choices(mode=[
            app_commands.Choice(name="view", value=0),
            app_commands.Choice(name="set", value=1),
            app_commands.Choice(name="delete", value=2),
        ])
    async def guildprefix(self, ctx, mode:int, ipf:Optional[str]=""):
        if ipf == "@everyone" or ipf == "@here":
            await ctx.send("その文字列はprefixとして使えません。")
            return
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        prefixes = gs["prefix"]
        if mode == 0:
            await ctx.send(embed=ut.getEmbed("サーバーのprefix", f'```{",".join(prefixes)}```'))
        elif mode == 1:
            spf = prefixes + [ipf]
            await self.bot.cursor.execute(
                "UPDATE guilds SET prefix = %s WHERE id = %s", (json.dumps(spf), ctx.guild.id))
            await ctx.send(await ctx._("upf-add", ipf))
        elif mode == 2:
            prefixes.remove(ipf)
            await self.bot.cursor.execute(
                "UPDATE guilds SET prefix = %s WHERE id = %s", (json.dumps(prefixes), ctx.guild.id))
            await ctx.send(f"{ipf}を削除しました。")
        else:
            await ctx.send(embed=ut.getEmbed("不適切なモード選択", "`0`(view)または`1`(set)または`2`(delete)を指定してください。"))

    @setting_cmds.command(description="思惟奈ちゃんの一部場面でのサーバー言語設定")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(lang="設定言語")
    async def guildlang(self, ctx, lang:str):
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #gs = await self.bot.cursor.fetchone()
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if lang not in self.bot.translate_handler.supported_locales:
            await ctx.send(await ctx._("setl-cantuse"))
        else:
            await self.bot.cursor.execute(
                "UPDATE guilds SET lang = %s WHERE id = %s", (lang, ctx.guild.id))
            self.bot.translate_handler.update_language_cache(ctx.guild, lang)
            await ctx.send(await ctx._("setl-set"))

    @setting_cmds.command(description="思惟奈ちゃんのサーバーログの送信設定を行います。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.describe(channel="送信先チャンネル")
    async def sendlogto(self, ctx, channel:Optional[discord.TextChannel]):
        to = channel
        if ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120:
            if to:
                await self.bot.cursor.execute(
                    "UPDATE guilds SET sendlog = %s WHERE id = %s", (to.id, ctx.guild.id))
                n = ctx.guild.me.nick
                await ctx.guild.me.edit(nick="ニックネーム変更テスト")
                await asyncio.sleep(1)
                await ctx.guild.me.edit(nick=n)
                await asyncio.sleep(1)
                await ctx.send("変更しました。ニックネーム変更通知が送られているかどうか確認してください。")
            else:
                await self.bot.cursor.execute(
                    "UPDATE guilds SET sendlog = %s WHERE id = %s", (None, ctx.guild.id))
                await ctx.send("解除しました。")
        else:
            await ctx.send("このコマンドの使用には、管理者権限が必要です。")

    @setting_cmds.command(aliases=["言語設定", "言語を次の言語に変えて"],description="思惟奈ちゃんの一部場面でのサーバー言語設定")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.describe(lang="設定言語")
    async def userlang(self, ctx, lang:str):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if lang not in self.bot.translate_handler.supported_locales:
            await ctx.send(await ctx._("setl-cantuse"))
        else:
            await self.bot.cursor.execute(
                "UPDATE users SET lang = %s WHERE id = %s", (lang, ctx.author.id))
            self.bot.translate_handler.update_language_cache(ctx.author, lang)
            await ctx.send(await ctx._("setl-set"))

    @commands.hybrid_command(description="指定されたコマンドに対して、利用制限をかけることができます。")
    @app_commands.describe(mode="使用するモード")
    @app_commands.describe(comname="(add/del)制限をかける/解除するコマンドの名前")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    async def comlock(self, ctx, mode: Literal['add', 'del', 'view'], comname:Optional[str]):
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        locks = json.loads(gs["lockcom"])
        #gs = await self.bot.cursor.fetchone()
        if mode == "add":
            if not comname:
                return await ctx.send("コマンド名が指定されていません！")
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(await ctx._("need-admin"))
                return
            # for i in comname:
            locks.append(comname)
            await self.bot.cursor.execute(
                "UPDATE guilds SET lockcom = %s WHERE id = %s", (json.dumps(locks), ctx.guild.id))
            await ctx.send(await ctx._("upf-add", str(comname)))
        elif mode == "del":
            if not comname:
                return await ctx.send("コマンド名が指定されていません！")
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 404243934210949120):
                await ctx.send(await ctx._("need-admin"))
                return
            # for i in comname:
                # try:
            locks.remove(comname)
                # except:
                    # pass
            await self.bot.cursor.execute(
                "UPDATE guilds SET lockcom = %s WHERE id = %s", (json.dumps(locks), ctx.guild.id))
            await ctx.send(await ctx._("deleted-text"))
        elif mode == "view":
            await ctx.send(await ctx._("comlock-view", gs["lockcom"]))

    @setting_cmds.command(aliases=["setsysmsg"],description="メンバーの参加、退出時のメッセージ設定")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.describe(mode="どうするか")
    @app_commands.describe(when="送信を行うとき")
    @app_commands.describe(channel="送信先チャンネル")
    @app_commands.describe(content="送信文字列")
    @app_commands.choices(mode=[
            app_commands.Choice(name="view", value=0),
            app_commands.Choice(name="set", value=1),
        ])
    @app_commands.choices(when=[
            app_commands.Choice(name="join", value="welcome"),
            app_commands.Choice(name="leave", value="cu")
        ])
    @app_commands.choices(channel=[
            app_commands.Choice(name="system_channel", value="sysch"),
            app_commands.Choice(name="dm", value="dm")
        ])
    async def set_action_msg(self, ctx, mode:int, when:Optional[str]="welcome", channel:Optional[str]="sysch", *, content:Optional[str]):
        to = channel
        msgs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #msgs = await self.bot.cursor.fetchone()
        sm = json.loads(msgs["jltasks"])
        if mode == 0:
            embed = discord.Embed(title=await ctx._(
                "ssm-sendcontent"), description=ctx.guild.name, color=self.bot.ec)
            try:
                embed.add_field(name=await ctx._(
                    "ssm-welcome"), value=f'{sm["welcome"].get("content")}({await ctx._("ssm-sendto")}):{sm["welcome"].get("sendto")})')
            except:
                pass
            try:
                embed.add_field(name=await ctx._(
                    "ssm-seeyou"), value=f'{sm["cu"].get("content")}({await ctx._("ssm-sendto")}:{sm["cu"].get("sendto")})')
            except:
                pass
            await ctx.send(embed=embed)
        elif mode == 1:
            if ctx.channel.permissions_for(ctx.author).administrator is True or ctx.author.id == 404243934210949120:
                try:
                    sm[when] = {}
                    sm[when]["content"] = content
                    sm[when]["sendto"] = to
                    await self.bot.cursor.execute(
                        "UPDATE guilds SET jltasks = %s WHERE id = %s", (json.dumps(sm), ctx.guild.id))
                    await ctx.send(await ctx._("ssm-set"))
                except:
                    await ctx.send(await ctx._("ssm-not"))
            else:
                await ctx.send(await ctx._("need-admin"))

    @setting_cmds.command(aliases=["サーバーコマンド", "次の条件でサーバーコマンドを開く"],description="サーバー独自の応答コマンドを作成できます。(prefixコマンドでのみ呼び出せます。)")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.describe(mode="どうするか")
    @app_commands.describe(name="コマンド名")
    @app_commands.choices(mode=[
            app_commands.Choice(name="add", value=0),
            app_commands.Choice(name="help", value=1),
            app_commands.Choice(name="all", value=2),
            app_commands.Choice(name="delete", value=3)
        ])
    async def servercmd(self, ctx, mode:int, name:Optional[str]):
        mmj = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #mmj = await self.bot.cursor.fetchone()
        cmds = json.loads(mmj["commands"])
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        if mode == 0:
            if not cmds.get(name, None) is None:
                if not(ctx.channel.permissions_for(ctx.author).manage_guild is True and ctx.channel.permissions_for(ctx.author).manage_roles is True or ctx.author.id == 404243934210949120):
                    await ctx.send(await ctx._("need-manage"))
                    return
            dc = ctx.author.dm_channel
            if dc is None:
                await ctx.author.create_dm()
                dc = ctx.author.dm_channel

            emojis = ctx.guild.emojis

            se = [str(i) for i in emojis]

            await dc.send(await ctx._("scmd-add-guide1"))

            def check(m):
                return m.channel == dc and m.author == ctx.author

            msg = await self.bot.wait_for('message', check=check)
            if msg.content == "one":
                await dc.send(await ctx._("scmd-add-guide2"))
                mes = await self.bot.wait_for('message', check=check)
                guide = mes.content
                try:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), str(se)))
                except:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), "(絵文字が多すぎて表示できません！)"))
                mg = await self.bot.wait_for('message', check=check)
                rep = mg.clean_content.format(se)
                cmds[name] = {}
                cmds[name]["mode"] = "one"
                cmds[name]["rep"] = rep
                cmds[name]["createdBy"] = ctx.author.id
                cmds[name]["guide"] = guide
            elif msg.content == "random":
                await dc.send(await ctx._("scmd-add-guide2"))
                mes = await self.bot.wait_for('message', check=check)
                guide = mes.content
                try:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), str(se)))
                except:
                    await dc.send(await ctx._("scmd-add-guide3-a", await ctx._("scmd-guide-emoji"), "(絵文字が多すぎて表示できません！)"))
                rep = []
                while True:
                    mg = await self.bot.wait_for('message', check=check)
                    if mg.content == "stop":
                        break
                    else:
                        rep = rep + [mg.clean_content.format(se)]
                        try:
                            await dc.send(await ctx._("scmd-add-guide3-b", await ctx._("scmd-guide-emoji"), str(se)))
                        except:
                            await dc.send(await ctx._("scmd-add-guide3-b", await ctx._("scmd-guide-emoji"), "(絵文字が多すぎて表示できません！)"))
                cmds[name] = {}
                cmds[name]["mode"] = "random"
                cmds[name]["rep"] = rep
                cmds[name]["createdBy"] = ctx.author.id
                cmds[name]["guide"] = guide
            elif msg.content == "role":
                if ctx.channel.permissions_for(ctx.author).manage_guild is True and ctx.channel.permissions_for(ctx.author).manage_roles is True or ctx.author.id == 404243934210949120:
                    await dc.send(await ctx._("scmd-add-guide2"))
                    mes = await self.bot.wait_for('message', check=check)
                    guide = mes.content
                    await dc.send(await ctx._("scmd-add-guide3-c", await ctx._("scmd-guide-emoji"), str(se)))
                    mg = await self.bot.wait_for('message', check=check)
                    rep = int(mg.clean_content)
                    cmds[name] = {}
                    cmds[name]["mode"] = "role"
                    cmds[name]["rep"] = rep
                    cmds[name]["createdBy"] = ctx.author.id
                    cmds[name]["guide"] = guide
                else:
                    await ctx.send(await ctx._("need-manage"))
                    return
            else:
                await dc.send(await ctx._("scmd-add-not"))
                return
            await self.bot.cursor.execute(
                "UPDATE guilds SET commands = %s WHERE id = %s", (json.dumps(cmds), ctx.guild.id))
            await ctx.send(await ctx._("scmd-add-fin"))
        elif mode == 1:
            if cmds == {}:
                await ctx.send(await ctx._("scmd-all-notfound"))
            elif cmds.get(name) is None:
                await ctx.send(await ctx._("scmd-help-notfound"))
            else:
                if isinstance(cmds[name]['createdBy'], int):
                    await ctx.send(await ctx._("scmd-help-title", name, await self.bot.fetch_user(cmds[name]['createdBy']), cmds[name]['guide']))
                else:
                    await ctx.send(await ctx._("scmd-help-title", name, cmds[name]['createdBy'], cmds[name]['guide']))
        elif mode == 2:
            if cmds == {}:
                await ctx.send(await ctx._("scmd-all-notfound"))
            else:
                await ctx.send(str(cmds.keys()).replace("dict_keys(", await ctx._("scmd-all-list")).replace(")", ""))
        elif mode == 3:
            if ctx.channel.permissions_for(ctx.author).manage_guild is True and ctx.channel.permissions_for(ctx.author).manage_roles is True or ctx.author.id == 404243934210949120:
                if not cmds is None:
                    del cmds[name]
                await ctx.send(await ctx._("scmd-del"))
                await self.bot.cursor.execute(
                    "UPDATE guilds SET commands = %s WHERE id = %s", (json.dumps(cmds), ctx.guild.id))
            else:
                await ctx.send(await ctx._("need-manage"))
        else:
            await ctx.send(await ctx._("scmd-except"))

    @commands.hybrid_command(description="ハッシュタグとしてチャンネルを使用する設定を切り替えます。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def hashtag(self, ctx):
        d = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        #d = await self.bot.cursor.fetchone()
        hc = json.loads(d["hash"])
        if hc == None:
            hc = [ctx.channel.id]
            await ctx.send(await ctx._("hash-connect"))
        elif ctx.channel.id in hc:
            hc.remove(ctx.channel.id)
            await ctx.send(await ctx._("hash-disconnect"))
        else:
            hc.append(ctx.channel.id)
            await ctx.send(await ctx._("hash-connect"))
        await self.bot.cursor.execute(
            "UPDATE guilds SET hash = %s WHERE id = %s", (json.dumps(hc), ctx.guild.id))

    # @commands.command(aliases=["オンライン通知"])
    # moved to apple_onlinenotif

    @setting_cmds.command(description="レベルアップ通知の送信先を変更できます。")
    @ut.runnable_check()
    @ut.runnable_check_for_appcmd()
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(to="送信先チャンネル")
    async def levelupsendto(self, ctx, to:Optional[discord.TextChannel]):
        if to is None:
            await self.bot.cursor.execute(
                "UPDATE guilds SET levelupsendto = %s WHERE id = %s", (0, ctx.guild.id))
        else:
            await self.bot.cursor.execute(
                "UPDATE guilds SET levelupsendto = %s WHERE id = %s", (to.id, ctx.guild.id))
        await ctx.send(await ctx._("changed"))

    
    @setting_cmds.command(description="機能の有効化設定")
    @ut.runnable_check()
    @app_commands.describe(feature_name="設定する機能")
    @app_commands.describe(enable="有効にするかどうか")
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_features(self, ctx, feature_name: Literal["level_count", "send_hashtag", "server_command", "default_prefix", "profile_reaction"], enable: bool = True):
        text_to_comlock = {
            "level_count":"clevel",
            "send_hashtag":"shash",
            "server_command":"scom",
            "default_prefix":"disable_defprefix",
            "profile_reaction":"disable_profile_msg"
        }
        # comlockに上記テキストが__含まれると__無効化される
        gs = await self.bot.cursor.fetchone(
            "select * from guilds where id=%s", (ctx.guild.id,))
        locks: list = json.loads(gs["lockcom"])
        if enable:
            # 含まれるなら削除する
            if text_to_comlock[feature_name] in locks:
                locks.remove(text_to_comlock[feature_name])
        else:
            # 含まれないなら追加する
            if not (text_to_comlock[feature_name] in locks):
                locks.append(text_to_comlock[feature_name])
        await self.bot.cursor.execute(
                "UPDATE guilds SET lockcom = %s WHERE id = %s", (json.dumps(locks), ctx.guild.id))
        await ctx.send(f"機能`{feature_name}`を{'有効' if enable else '無効'}にしました。")



async def setup(bot):
    await bot.add_cog(settings(bot))
