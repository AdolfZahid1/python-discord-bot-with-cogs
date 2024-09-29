from typing import Tuple, Union, Any
import logging
import asyncio
import re
import psycopg2.extras


class PostgresConnection:
    """Describe connections to postgres"""
    connect = psycopg2.connect(database="postgres", user="postgres", password="#nUKb9aCc&9", host="localhost",
                               port="5432")
    logging.info("connected to Postgres")
    cur = connect.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


async def add_balance(member: int, arg: int) -> bool:
    """Add money to users bank"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"UPDATE users SET user_bank = user_bank + {arg} WHERE user_id = {member}")
        conn.commit()
        conn.close()
        logging.info("Successfully added balance to {member} bank")
        return True
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def remove_balance(member: int, arg: int) -> bool:
    """Remove amount from users bank balance"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"UPDATE users SET user_bank = user_bank - {arg} WHERE user_id = {member}")
        conn.commit()
        conn.close()
        logging.info(f"Removed balance from {member} bank")
        return True
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def get_balance(member: int) -> tuple[int, int]:
    """Get users balance from database"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"SELECT user_bank,user_cash FROM users WHERE user_id = {member}")
        result1 = list(cur.fetchall())
        result = []
        for s in re.findall(r'\b\d+\b', str(result1[0])):
            result.append(int(s))
        conn.close()
        logging.info(f"Got balance of {member}")
        return int(result[0]), int(result[1])
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def insert_member(member: int,guild_id: int) -> None:
    """Add member to table"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"SELECT user_id FROM users WHERE user_id = {member};")
        result = cur.fetchall()
        conn.commit()
        if len(result) == 0:
            cur.execute(f"INSERT INTO users (user_id,user_bank,user_cash,guild_id) VALUES ({member},0,0,{guild_id})")
        conn.commit()
        logging.info(f"Added member {member} to table users")
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def deposit(member: int) -> bool:
    """Deposit members money to bank from cash"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"UPDATE users SET user_bank = user_bank + user_cash,user_cash = 0 WHERE user_id = {member}")
        conn.commit()
        conn.close()
        logging.info(f"{member} deposited to bank")
        return True
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def rob(ctx: int, member: int) -> bool:
    """Rob user"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"SELECT user_cash FROM users WHERE user_id = {member}")
        balance = int(cur.fetchall()[0])
        other_user_cash = f"(SELECT user_cash FROM users WHERE user_id = {member})"
        if balance > 0:
            cur.execute(f"UPDATE users SET user_bank = user_bank + {other_user_cash} WHERE user_id = {ctx}")
            cur.execute(f"UPDATE users SET user_cash = 0 where user_id = {member}")
            conn.commit()
            conn.close()
            logging.info(f"{ctx} robbed user {member} for {other_user_cash}")
            return True
        return False
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def withdraw(ctx: int, amount: int) -> bool:  # type: ignore
    """Withdraw money from members bank to cash"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"SELECT user_bank FROM users WHERE user_id = {ctx}")
        bank = cur.fetchall()[0]
        if bank >= amount:
            cur.execute(f"UPDATE users SET user_bank = user_bank - {amount} WHERE user_id = {ctx}")
            cur.execute(f"UPDATE users SET user_cash = user_cash + {amount} where user_id = {ctx}")
            conn.commit()
            conn.close()
            logging.info(f"{ctx} withdrawed {amount} from his bank")
            return True
        return False
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def top() -> list:
    """Get top users from table"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"SELECT user_id,user_bank FROM users ORDER BY user_bank DESC")

        async def fetch(row):
            await asyncio.sleep(1)
            new_string = ""
            new_string += f"<@{row['user_id']}>\t{row['user_bank']}\n"
            return new_string

        conn.commit()
        coro = [fetch(row) for row in cur.fetchall()]
        result = await asyncio.gather(*coro)
        return result
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def set_balance(member: int, amount: int) -> bool:
    """Set balance for a member"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"UPDATE users SET balance = {amount} WHERE user_id = {member}")
        conn.commit()
        conn.close()
        logging.info(f"Set balance of {member} to {amount}")
        return True
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


async def reset_balance(member: int) -> bool:
    """Reset balance for a member"""
    try:
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
        cur.execute(f"UPDATE users SET user_bank,user_cash = 0 WHERE user_id = {member}")
        conn.commit()
        conn.close()
        logging.info(f"Reset balance of {member} to 0")
        return True
    except psycopg2.InterfaceError:
        logging.warning(psycopg2.InterfaceError)
        conn = PostgresConnection.connect
        cur = PostgresConnection.cur
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
