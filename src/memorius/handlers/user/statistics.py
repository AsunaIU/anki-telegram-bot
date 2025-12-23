from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from memorius.database.repositories import StatisticsRepository
from memorius.keyboards.keyboards import get_statistics_period_keyboard

router = Router()


@router.message(
    F.text.in_(
        [
            "📊 Статистика",  # Russian
            "📊 Statistics",  # English
        ]
    )
)
async def show_statistics_menu(message: Message, locale: TranslatorRunner):
    """Show statistics menu"""
    await message.answer(locale.select_period(), reply_markup=get_statistics_period_keyboard(locale))


@router.callback_query(F.data.startswith("stats_"))
async def show_statistics(callback: CallbackQuery, session: AsyncSession, locale: TranslatorRunner):
    """Show statistics for selected period"""
    days = int(callback.data.split("_")[1])

    stats_repo = StatisticsRepository(session)
    stats = await stats_repo.get_user_statistics(user_id=callback.from_user.id, days=days)

    total = stats["total"]
    easy = stats["easy"]
    medium = stats["medium"]
    hard = stats["hard"]
    skipped = stats["skipped"]

    if total == 0:
        text = locale.stats_for_period(days=days) + "\n\n"
        text += locale.no_stats()
    else:
        successful = easy
        need_review = medium + hard

        text = locale.stats_for_period(days=days) + "\n\n"
        text += locale.stats_details(
            total=total,
            successful=successful,
            need_review=need_review,
            skipped=skipped,
            easy=easy,
            medium=medium,
            hard=hard,
        )

        if successful > 0:
            success_rate = (successful / total) * 100
            text += "\n\n" + locale.success_rate(rate=f"{success_rate:.1f}")

        text += "\n\n" + locale.keep_going()

    await callback.message.edit_text(text, reply_markup=get_statistics_period_keyboard(locale))
    await callback.answer()
