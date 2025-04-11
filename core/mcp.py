import os
import requests
from pydantic import BaseModel, Field


class MCPResult(BaseModel):
    """
    MCP 返回结果格式

    Attributes:
        status (str): 查询状态，如 "success" 或 "error"
        data (dict): 返回的数据信息
        error (str): 出错时的错误描述
    """
    status: str = Field(..., description="查询状态")
    data: dict = Field(default_factory=dict, description="查询返回的数据")
    error: str = Field("", description="错误信息")


def query_mcp_data(query: str) -> MCPResult:
    """
    调用 MCP 平台查询医疗数据，并返回结构化结果

    Args:
        query (str): 查询语句或关键词

    Returns:
        MCPResult: 包含状态、数据及错误信息的结果
    """
    mcp_api_url = os.getenv("MCP_API_URL", "https://api.mcp.example/query")
    mcp_api_key = os.getenv("MCP_API_KEY", "your_mcp_api_key")
    headers = {
        "Authorization": f"Bearer {mcp_api_key}",
        "Content-Type": "application/json",
    }
    payload = {"query": query, "extra_config": os.getenv("MCP_EXTRA_CONFIG", "")}
    try:
        response = requests.post(mcp_api_url, headers=headers, json=payload)
        if response.ok:
            return MCPResult(status="success", data=response.json())
        else:
            return MCPResult(status="error", error=response.text)
    except Exception as e:
        return MCPResult(status="error", error=str(e))
