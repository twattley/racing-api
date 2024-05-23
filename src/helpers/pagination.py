from pydantic import AnyUrl
from starlette.datastructures import URL

from ..models.pagination_links import PaginationLinks


def build_pagination_links(
    url: URL, limit: int, page: int, has_more_data: bool
) -> PaginationLinks:
    prev_url = (
        url.include_query_params(page=page - 1, limit=limit) if page > 1 else None
    )
    next_url = (
        url.include_query_params(page=page + 1, limit=limit) if has_more_data else None
    )

    return PaginationLinks(
        self=AnyUrl(url=str(url)),
        prev=AnyUrl(url=str(prev_url)) if prev_url else None,
        next=AnyUrl(url=str(next_url)) if next_url else None,
    )
