from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.repositories import UserRepository
from memorius.keyboards import get_contact_keyboard, get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, locale: TranslatorRunner):
    """Handle /start command"""
    user_repo = UserRepository(session)

    user = await user_repo.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    if user.phone_number:
        await message.answer(locale.welcome_message(), reply_markup=get_main_menu_keyboard(locale))
    else:
        await message.answer(locale.welcome_message(), reply_markup=get_contact_keyboard(locale))


@router.message(F.contact)
async def process_contact(message: Message, session: AsyncSession, locale: TranslatorRunner):
    """Process shared contact"""
    if message.contact.user_id == message.from_user.id:
        user_repo = UserRepository(session)
        await user_repo.update_phone(user_id=message.from_user.id, phone_number=message.contact.phone_number)

        await message.answer(locale.registration_success(), reply_markup=get_main_menu_keyboard(locale))
    else:
        await message.answer(locale.registration_share_contact(), reply_markup=get_contact_keyboard(locale))


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, locale: TranslatorRunner):
    await callback.message.answer(locale.main_menu(), reply_markup=get_main_menu_keyboard(locale))
    await callback.message.delete()
    await callback.answer()
