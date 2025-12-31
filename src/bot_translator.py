import discord
from discord import app_commands
from src.translator import Translator, Lang


class BotTranslator(app_commands.Translator):
    def __init__(self):
        self.translators = {
            discord.Locale.korean: Translator(lang=Lang.KO),
            discord.Locale.american_english: Translator(lang=Lang.EN),
            # add another languages
        }
        self.default_translator = Translator(lang=Lang.EN)

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext,
    ) -> str | None:

        key = string.message

        # commands name
        if context.location == app_commands.TranslationContextLocation.command_name:
            # 'key' is defined in extras --> Use that value as the primary key
            # ex) extras={"key": "cmd.duviri-circuit.inc-cmd"}
            if (
                isinstance(context.data, (app_commands.Command, app_commands.Group))
                and "key" in context.data.extras
            ):
                key = context.data.extras["key"]
            else:
                # no extras, default rule
                key = f"cmd.{string.message}.cmd"

        # parameter name
        elif context.location == app_commands.TranslationContextLocation.parameter_name:
            cmd_name = context.data.command.name
            param_name = string.message.replace("_", "-")
            key = f"cmd.{cmd_name}.arg-{param_name}"

        # description
        elif context.location in (
            app_commands.TranslationContextLocation.command_description,
            app_commands.TranslationContextLocation.parameter_description,
        ):
            key = string.message

        translator = self.translators.get(locale, self.default_translator)
        translated = translator.get(key)

        # retry if trnaslation failed
        if translated == key:
            translated = self.default_translator.get(key)
            if translated == key:
                return None

        return translated
