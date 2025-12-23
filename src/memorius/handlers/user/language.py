from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorHub, TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.repositories import UserRepository
from memorius.keyboards import get_language_keyboard, get_main_menu_keyboard

router = Router()


@router.message(F.text.in_(["🌐 Язык", "🌐 Language"]))
async def show_language_menu(
    message: Message,
    locale: TranslatorRunner,
):
    await message.answer(
        locale.select_language(),
        reply_markup=get_language_keyboard(locale),
    )


@router.callback_query(F.data.startswith("lang_"))
async def change_language(
    callback: CallbackQuery,
    session: AsyncSession,
    t_hub: TranslatorHub,
):
    language_code = callback.data.split("_", 1)[1]

    user_repo = UserRepository(session)
    await user_repo.update_language(
        user_id=callback.from_user.id,
        language_code=language_code,
    )

    new_locale = t_hub.get_translator_by_locale(language_code)

    await callback.message.delete()

    await callback.message.answer(
        new_locale.language_changed(),
        reply_markup=get_main_menu_keyboard(new_locale),
    )

    await callback.answer()
