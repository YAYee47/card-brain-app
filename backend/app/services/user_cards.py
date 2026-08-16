from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cards import Card
from app.models.user_cards import UserCard


async def get_card_by_id(db: AsyncSession, card_id: int):
    result = await db.execute(get_card_by_id_query(card_id))
    return result.scalar_one_or_none()


async def get_user_card_by_id(db: AsyncSession, user_card_id: int, user_id: int):
    result = await db.execute(get_user_card_detail_query(user_card_id, user_id))
    return result.scalar_one_or_none()


async def get_active_user_card(db: AsyncSession, user_card_id: int, user_id: int):
    result = await db.execute(
        select(UserCard)
        .where(UserCard.id == user_card_id, UserCard.is_active == True, UserCard.user_id == user_id)
        .options(selectinload(UserCard.card))
    )
    return result.scalar_one_or_none()


def get_card_list_query():
    return select(Card).options(selectinload(Card.benefits))


def get_card_by_id_query(card_id: int):
    return select(Card).where(Card.id == card_id).options(selectinload(Card.benefits))


def get_active_user_cards_query(user_id: int):
    return (
        select(UserCard)
        .where(UserCard.is_active == True, UserCard.user_id == user_id)
        .options(selectinload(UserCard.card).selectinload(Card.benefits))
    )


def get_user_card_detail_query(user_card_id: int, user_id: int):
    return (
        select(UserCard)
        .where(UserCard.id == user_card_id, UserCard.user_id == user_id)
        .options(selectinload(UserCard.card).selectinload(Card.benefits))
    )


def get_user_card_with_card_only_query(user_card_id: int, user_id: int):
    return select(UserCard).where(UserCard.id == user_card_id, UserCard.user_id == user_id).options(selectinload(UserCard.card))


def get_same_bank_user_cards_query(bank_name: str, user_id: int):
    return select(UserCard).join(Card).where(Card.bank_name == bank_name, UserCard.user_id == user_id)
