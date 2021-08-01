from django.urls import path
from .views import (
    ActiveListings,
    ListingDetails,
    CreateListing,
    UpdateComment,
    DeleteComment,
    ViewWatchList,
    CloseBidding,
    ClosedListings,
    categories,
    display_categories,
)

urlpatterns = [
    path("", ActiveListings.as_view(), name="listings"),
    path("create/", CreateListing.as_view(), name="create"),
    path("closed/", ClosedListings.as_view(), name="closed"),
    path("watchlist/", ViewWatchList.as_view(), name="watchlist"),
    path("categories/", categories, name="categories"),
    path("listings/<int:pk>/", ListingDetails.as_view(), name="details"),
    path("listings/<int:pk>/close/", CloseBidding.as_view(), name="close"),
    path(
        "listings/comments/<int:pk>/update/",
        UpdateComment.as_view(),
        name="update-comment",
    ),
    path(
        "listings/comments/<int:pk>/delete/",
        DeleteComment.as_view(),
        name="delete-comment",
    ),
    path("listings/categories/<str:category>/", display_categories, name="display"),
]
