document.addEventListener('DOMContentLoaded', () => {
    const auctionGallery = document.getElementById('auction-gallery');
    const artworkCount = auctionGallery.getElementsByClassName('auction-item').length;

    document.getElementById('artwork-count').textContent = artworkCount;
    document.getElementById('auction-artwork-count').textContent = artworkCount;
});
