from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import (
    Listing,
    WatchList,
    Bid,
    Comment,
    CHOICES,
)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import CreateListingForm, CommentUpdateForm, CloseBiddingForm
from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist

# Create your views here.


def categories(request):

    categories_ = []

    for category in CHOICES:
        categories_.append(f"{category[0][0].upper()}{category[0][1:]}")

    if request.method == "POST":
        if "category" in request.POST:
            category = request.POST["category"]
            return HttpResponseRedirect(reverse("display", args=(category.lower(),)))

    context = {"categories": categories_}

    return render(request, "auctions/categories.html", context)


def display_categories(request, category):

    context = {}

    listings = Listing.objects.filter(category=category, is_closed=False)
    bids = Bid.arg_max(queryset=listings)
    try:
        listings = list((zip(reversed(listings), bids)))
        context["listings"] = listings
    except TypeError:
        context["listings"] = None

    context = {"listings": listings, "bid": bids}

    return render(request, "auctions/active_listings.html", context)


class CreateListing(LoginRequiredMixin, CreateView):
    model = Listing
    template_name = "auctions/create_listing.html"
    context_object_name = "form"
    form_class = CreateListingForm

    def post(self, request, *args, **kwargs):

        bid = self.request.POST.get("bid")
        user = self.request.user
        title = self.request.POST.get("title")
        description = self.request.POST.get("description")
        category = self.request.POST.get("category")
        if self.request.POST.get("image_url"):

            image_url = self.request.POST.get("image_url")

            try:
                instance = Listing.objects.create(
                    seller=user,
                    title=title,
                    bid=bid,
                    description=description,
                    category=category,
                    image_url=image_url,
                )
                Bid.objects.create(listing_key=instance, bid=bid)
                messages.success(request, "Successfully created your listing")

                return HttpResponseRedirect(reverse("listings"))
            except IntegrityError:
                messages.error(request, "Title must be unique")

                return HttpResponseRedirect(reverse("create"))
        else:

            try:
                instance = Listing.objects.create(
                    seller=user,
                    title=title,
                    bid=bid,
                    description=description,
                    category=category,
                )
                Bid.objects.create(listing_key=instance, bid=bid)
                messages.success(request, "Successfully created your listing")

                return HttpResponseRedirect(reverse("listings"))
            except IntegrityError:
                messages.error(request, "Title must be unique")

                return HttpResponseRedirect(reverse("create"))


class ActiveListings(LoginRequiredMixin, ListView):
    model = Listing
    context_object_name = "listings"
    ordering = "-date"
    template_name = "auctions/active_listings.html"
    queryset = Listing.objects.filter(is_closed=False)

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(**kwargs)
        bids = Bid.arg_max(queryset=self.get_queryset())
        listings_ = Listing.objects.filter(is_closed=False)
        try:
            listings = list((zip(reversed(listings_), bids)))
            context["listings"] = listings
        except TypeError:
            context["listings"] = None

        return context


class ClosedListings(LoginRequiredMixin, ListView):
    model = Bid
    context_object_name = "bids"
    template_name = "auctions/closed_listings.html"
    ordering = "-date   "

    def get_queryset(self):

        return Bid.objects.filter(is_closed=True)


class ListingDetails(LoginRequiredMixin, DetailView):
    model = Listing
    context_object_name = "obj"
    template_name = "auctions/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        listing_bid = Bid.arg_max(
            key=self.get_object()
        )  # return the bid object for the listing
        # gets the comments for the listing
        comments = Comment.objects.filter(listing_key=self.get_object()).order_by(
            "-date"
        )
        obj = Listing.objects.get(is_closed=False, pk=self.get_object().pk)
        try:
            watch_list = WatchList.objects.get(
                user=self.request.user, listing_key=self.get_object()
            )
            context["list"] = watch_list.is_watched
        except (ObjectDoesNotExist, IndexError):
            context["list"] = None

        context["obj"] = obj
        context["bid"] = listing_bid
        context["comments"] = comments

        return context

    def post(self, request, *args, **kwargs):
        # get the post data and process it

        if self.request.POST.get("bid"):

            try:
                bid = float(self.request.POST.get("bid"))
            except ValueError:
                messages.error(request, "Invalid input for Bid")

                return HttpResponseRedirect(
                    reverse("details", args=(self.get_object().pk,))
                )

            current_bid = Bid.arg_max(key=self.get_object()).bid

            if bid > current_bid:
                obj = Bid()
                obj.user = self.request.user
                obj.bid = bid
                obj.listing_key = self.get_object()
                obj.save()

                messages.success(request, "Bid placed successfully")

                return HttpResponseRedirect(
                    reverse("details", args=(self.get_object().pk,))
                )
            else:
                messages.error(request, "Bid must be higher than current bid")
                return HttpResponseRedirect(
                    reverse("details", args=(self.get_object().pk,))
                )

        elif self.request.POST.get("comment"):

            comment = self.request.POST.get("comment")

            comment_ = Comment()
            comment_.content = comment
            comment_.author = self.request.user
            comment_.listing_key = self.get_object()
            comment_.save()

            messages.success(request, "Comment added successfully")

            return HttpResponseRedirect(
                reverse("details", args=(self.get_object().pk,))
            )

        elif "watch" in self.request.POST:

            watch_list, created = WatchList.objects.get_or_create(
                user=self.request.user
            )
            watch_list.is_watched = True
            watch_list.listing_key.add(self.get_object())
            watch_list.save()

            messages.success(
                request, f"Successfully added {self.get_object().title} to Watch list"
            )

            return HttpResponseRedirect(
                reverse("details", args=(self.get_object().pk,))
            )

        elif "remove" in self.request.POST:
            results = WatchList.objects.filter(user=self.request.user)
            rm = results[0].listing_key.all()
            results[0].listing_key.remove(rm[0].pk)

            messages.success(request, "Removed listing from Watch list")

            return HttpResponseRedirect(
                reverse("details", args=(self.get_object().pk,))
            )

        return self.get(self, request, *args, **kwargs)


class UpdateComment(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    context_object_name = "form"
    form_class = CommentUpdateForm
    template_name = "auctions/comment_update.html"

    def get_success_url(self):

        return reverse("details", args=(self.get_object().listing_key.pk,))

    def form_valid(self, form):

        form.instance.author = self.request.user

        return super(UpdateComment, self).form_valid(form)

    def test_func(self):

        comment = self.get_object()

        if comment.author == self.request.user:
            return True
        else:
            return False


class CloseBidding(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "auctions/close.html"
    model = Listing
    context_object_name = "obj"
    form_class = CloseBiddingForm

    def post(self, request, *args, **kwargs):

        if "close" in self.request.POST:
            listing = self.get_object()
            listing.is_closed = True
            listing.save()

            bid = Bid.arg_max(key=listing)
            bid.is_closed = True
            bid.save()

            messages.info(request, "Auction closed successfully")

            return HttpResponseRedirect(reverse("closed"))

        return self.get(self, request, *args, **kwargs)

    def test_func(self):
        listing = self.get_object()

        if listing.seller == self.request.user:
            return True
        else:
            return False


class DeleteComment(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "auctions/comment_delete.html"
    context_object_name = "comment"

    def test_func(self):
        comment = self.get_object()

        if comment.author == self.request.user:
            return True
        else:
            return False

    def get_success_url(self):

        messages.success(self.request, "Deleted comment")

        return reverse("details", args=(self.get_object().listing_key.pk,))


class ViewWatchList(LoginRequiredMixin, ListView):
    model = WatchList
    template_name = "auctions/watchlist.html"
    context_object_name = "listings"

    def get_queryset(self):

        objects = []

        for object_ in WatchList.objects.filter(user=self.request.user):
            objects.append(object_.listing_key.all())

        return objects
