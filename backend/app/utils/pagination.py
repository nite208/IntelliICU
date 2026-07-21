"""
Pagination utilities.
"""

from math import ceil


def paginate(
    items,
    page: int = 1,
    page_size: int = 10,
):
    """
    Simple pagination helper.
    """

    total = len(items)

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if total else 1,
    }