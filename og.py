import asyncio
import logging
from ourgroceries import OurGroceries
import config

# Configure basic logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _get_or_create_list(og: OurGroceries, list_name: str) -> str:
    """
    Fetch existing shopping lists and return the ID of the one matching list_name.
    If not found, create a new list (type=SHOPPING) and return its ID.
    Raises RuntimeError on any OG API failure.
    """
    # 1) Attempt to fetch all lists container
    try:
        resp = await og.get_my_lists()
        logger.debug(f"Fetched lists response: {resp}")
    except Exception as e:
        logger.exception("Failed to fetch lists from OurGroceries")
        raise RuntimeError(f"OurGroceries: failed to fetch lists: {e}") from e

    # 2) Extract shoppingLists array if present
    if isinstance(resp, dict):
        lists = resp.get("shoppingLists", [])
        logger.debug(f"Extracted shoppingLists: {lists}")
    else:
        lists = resp
        logger.debug(f"Using lists iterable: {lists}")

    # 3) Search for matching list entries
    for entry in lists:
        if not isinstance(entry, dict):
            logger.warning(f"Skipping non-dict list entry: {entry}")
            continue
        name = entry.get("name")
        lid = entry.get("id") or entry.get("listId")
        logger.debug(f"Checking shopping list: {{'name': {name}, 'id': {lid}}}")
        if name == list_name:
            logger.info(f"Found existing OurGroceries list '{list_name}' with ID {lid}")
            return lid

    # 4) Not found: attempt to create a new shopping list
    try:
        new_list = await og.create_list(list_name, list_type='SHOPPING')
        logger.info(f"create_list response: {new_list}")
    except Exception as e:
        logger.exception(f"Failed to create OurGroceries list '{list_name}'")
        raise RuntimeError(f"OurGroceries: failed to create list '{list_name}': {e}") from e

    # 5) Extract and return the new list ID
    if isinstance(new_list, dict):
        list_id = new_list.get("listId") or new_list.get("id")
        if not list_id:
            logger.error(f"Unexpected create_list response: {new_list}")
            raise RuntimeError(f"OurGroceries: create_list returned unexpected response: {new_list}")
        logger.info(f"Created new OurGroceries list '{list_name}' with ID {list_id}")
        return list_id

    # If create_list returned a raw ID string
    logger.info(f"Created new OurGroceries list '{list_name}' with raw ID {new_list}")
    return new_list

async def add_items_to_og(list_name: str, items: list[str]):
    """
    Log in, ensure the target shopping list exists (creating it if necessary),
    and send all items to it.

    Raises:
        RuntimeError: if any OurGroceries operation fails
    """
    try:
        logger.debug(f"Logging into OurGroceries as {config.OG_USERNAME}")
        og = OurGroceries(config.OG_USERNAME, config.OG_PASSWORD)
        await og.login()
        logger.debug("Login successful")

        list_id = await _get_or_create_list(og, list_name)
        logger.debug(f"Using OurGroceries list ID {list_id}")

        logger.debug(f"Adding items to OG list: {items}")
        await og.add_items_to_list(list_id, items)
        logger.info(f"Added {len(items)} items to OurGroceries list '{list_name}'")
    except Exception as e:
        logger.exception("Error syncing items to OurGroceries")
        # Provide context for failures
        raise RuntimeError(f"OurGroceries sync failed: {e}") from e

# Convenience synchronous wrapper

def send_items_to_og_sync(list_name: str, items: list[str]) -> tuple[bool, str | None]:
    """
    Run the async add_items_to_og from sync context.

    Returns:
        (success, error_message)
    """
    try:
        asyncio.run(add_items_to_og(list_name, items))
        return True, None
    except Exception as e:
        return False, str(e)
