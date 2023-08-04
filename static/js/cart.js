var updateBtns = document.getElementsByClassName('update-cart');
document.getElementById('add-to-cart-btn').addEventListener('click', function (event) {
    event.preventDefault();

    var selectElement = document.getElementById('size');
    var selectedVariantId = selectElement.value;
    var action = 'add';
    var productId = '{{ product.id }}'; // Use Django template tag to get the product ID
    console.log('Selected Variant ID:', selectedVariantId);
    console.log('Action:', action);
    console.log('Product ID:', productId);
    console.log('USER:', user);

    if (user === 'AnonymousUser') {
        console.log('User is not authenticated');
    } else {
        updateUserOrder(productId, action, selectedVariantId);
    }
});

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        var variantId = this.dataset.variant; // The attribute name should be 'data-variant', not 'data-variantId'
        var action = this.dataset.action;
        var productId = this.dataset.product; // Add this line to get the product ID
        console.log('variantId:', variantId, 'Action:', action);
        console.log('Product ID:', productId);
        console.log('USER:', user);

        if (user === 'AnonymousUser') {
            console.log('User is not authenticated');
        } else {
            updateUserOrder(productId, action, variantId); // Use the correct variable name
        }
    });
}

// JavaScript code for adding an item to the cart
function updateUserOrder(productId, action, variantId) {
    console.log('User is authenticated, sending data...');
    console.log('Product ID:', productId);
    console.log('Variant ID:', variantId);
    console.log('Action:', action);
    var url = '/update_item/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            productId: productId,
            action: action,
            variantId: variantId,
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        location.reload();
    });
}
