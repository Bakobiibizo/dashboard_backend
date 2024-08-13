import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from wallet.commands.comx_command_manager import ComxCommandManager

@pytest.fixture
def comx_manager():
    with patch('wallet.commands.comx_command_manager.CONFIG') as mock_config:
        mock_config.querymap_path = Path("/tmp/querymaps")
        mock_config.subnet_query_list = ["query_map_1", "query_map_2"]
        mock_config.subnets = [1, 2]
        mock_config.node_url = "http://localhost"
        with patch('wallet.commands.comx_command_manager.CommuneClient') as mock_client:
            with patch('wallet.commands.comx_command_manager.Wallet'):
                yield ComxCommandManager()

@pytest.mark.asyncio
async def test_init_manager(comx_manager):
    # Act
    await comx_manager.init_manager()

    # Assert

    assert comx_manager.commands
    assert comx_manager.commands_list

@pytest.mark.asyncio
async def test_check_path(comx_manager):
    path = Path("/tmp/test_path")

    # Act
    comx_manager.check_path(path)

    # Assert
    assert path.exists()

@pytest.mark.asyncio
async def test_get_command_list(comx_manager):
    # Act
    commands_list = await comx_manager.get_command_list()

    # Assert
    assert commands_list

@pytest.mark.asyncio
async def test_get_commands_dict(comx_manager):
    await comx_manager.get_command_list()

    # Act
    commands_dict = await comx_manager.get_commands_dict()

    # Assert
    assert commands_dict

@pytest.mark.asyncio
@pytest.mark.parametrize("command_name,kwargs,expected", [
    ("register", {}, "register_result"),
    ("transfer", {"amount": 100}, "transfer_result"),
], ids=["register", "transfer"])
async def test_execute_command(comx_manager, command_name, kwargs, expected):
    comx_manager.commands = {
        "register": AsyncMock(return_value="register_result"),
        "transfer": AsyncMock(return_value="transfer_result")
    }

    # Act
    result = await comx_manager.execute_command(command_name, **kwargs)

    # Assert
    assert result == expected

@pytest.mark.asyncio
async def test_execute_command_not_in_whitelist(comx_manager):
    comx_manager.commands = {
        "non_whitelisted_command": AsyncMock()
    }

    # Act / Assert
    with pytest.raises(ValueError):
        await comx_manager.execute_command("non_whitelisted_command")

@pytest.mark.asyncio
async def test_get_query_map_list(comx_manager):
    await comx_manager.get_command_list()

    # Act
    query_maps = await comx_manager.get_all_query_map()

    # Assert
    assert query_maps

@pytest.mark.asyncio
@pytest.mark.parametrize("query_map_name,kwargs,expected", [
    ("query_map_1", {}, "query_map_1_result"),
    ("query_map_2", {"param": "value"}, "query_map_2_result"),
], ids=["query_map_1", "query_map_2"])
async def test_execute_query_map(comx_manager, query_map_name, kwargs, expected):
    comx_manager.query_maps = {
        "query_map_1": AsyncMock(return_value="query_map_1_result"),
        "query_map_2": AsyncMock(return_value="query_map_2_result")
    }

    # Act
    result = await comx_manager.execute_query_map(query_map_name, **kwargs)

    # Assert
    assert result == expected

@pytest.mark.asyncio
async def test_execute_query_map_not_found(comx_manager):
    # Act / Assert
    with pytest.raises(ValueError):
        await comx_manager.execute_query_map("non_existent_query_map")

@pytest.mark.asyncio
async def test_get_all_query_map(comx_manager):
    comx_manager.querymap_path = Path("/tmp/querymaps")
    comx_manager.querymap_path.mkdir(parents=True, exist_ok=True)
    (comx_manager.querymap_path / "query_map_1.json").write_text(json.dumps({"key": "value"}))

    # Act
    query_maps = await comx_manager.get_all_query_map()

    # Assert
    assert query_maps

@pytest.mark.asyncio
async def test_get_subnet_maps(comx_manager):
    comx_manager.querymap_path = Path("/tmp/querymaps")
    comx_manager.querymap_path.mkdir(parents=True, exist_ok=True)
    (comx_manager.querymap_path / "query_map_1.json").write_text(json.dumps({"1": {"key": "value"}}))

    # Act
    subnet_maps = await comx_manager.get_subnet_maps(1)

    # Assert
    assert subnet_maps

@pytest.mark.asyncio
async def test_load_subnet_query_data(comx_manager):
    comx_manager.querymap_path = Path("/tmp/querymaps")
    file_path = comx_manager.querymap_path / "1" / "query_map_test.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps({"key": "value"}))

    # Act
    data = await comx_manager.load_subnet_query_data("test", 1)

    # Assert
    assert data == {"key": "value"}

@pytest.mark.asyncio
async def test_execute_all_query_map(comx_manager):
    
    # Act
    await comx_manager.execute_all_query_map()

    # Assert
    file_path = comx_manager.querymap_path
    assert file_path.exists()

@pytest.mark.asyncio
async def test_query_map_loop(comx_manager):
    comx_manager.execute_all_query_map = AsyncMock()
    comx_manager.execute_all_query_map.side_effect = [None, Exception("Test Exception")]

    # Act
    task = asyncio.create_task(comx_manager.query_map_loop())
    await asyncio.sleep(1)
    task.cancel()

    # Assert
    assert comx_manager.execute_all_query_map.call_count > 0
