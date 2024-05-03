from pydantic import AnyUrl
from starlette.datastructures import URL

from src.models.pagination_links import PaginationLinks


def build_pagination_links(url: URL, limit: int, page: int, has_more_data: bool) -> PaginationLinks:
    prev_url = url.include_query_params(limit=limit, page=page - 1)
    next_next = url.include_query_params(limit=limit, page=page + 1)
    return PaginationLinks(
        self=AnyUrl(url=url._url),
        prev=AnyUrl(url=prev_url._url) if page > 0 else None,
        next=AnyUrl(url=next_next._url) if has_more_data else None,
    )
