import React, { useState } from 'react';
import '../allCss/ShopPage.css';

const products = [
    { id: 1, name: 'LD01 LOUNGE CHAIR', price: 200, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
    { id: 2, name: 'LD02 LOUNGE CHAIR', price: 250, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
    { id: 3, name: 'LD03 LOUNGE CHAIR', price: 290, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
    { id: 4, name: 'LD04 LOUNGE CHAIR', price: 200, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
    { id: 5, name: 'LD05 LOUNGE CHAIR', price: 300, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
    { id: 6, name: 'LD06 LOUNGE CHAIR', price: 200, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
    { id: 7, name: 'LD07 LOUNGE CHAIR', price: 200, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
    { id: 8, name: 'LD08 LOUNGE CHAIR', price: 200, image: 'https://i1.adis.ws/i/ArsenalDirect/mit6141_f1?$pdpMainImage$' },
];

const ShopPage = () => {
    const [cart, setCart] = useState([]);
    const [showCart, setShowCart] = useState(false);

    const addToCart = (product) => {
        setCart([...cart, product]);
    };

    const toggleCart = () => {
        setShowCart(!showCart);
    };

    return (
        <div className="container">
            <header>
                <h1 className="title">Shop</h1>
                <div className="icon-cart" onClick={toggleCart}>
                    <svg viewBox="0 0 24 24">
                        <path fill="currentColor" d="M7 18c1.1046 0 2-.8954 2-2s-.8954-2-2-2-2 .8954-2 2 .8954 2 2 2zm10 0c1.1046 0 2-.8954 2-2s-.8954-2-2-2-2 .8954-2 2 .8954 2 2 2zm-1.333-5h-9.334l-.933-4h12.2l-1.933 4zm1.066-6h-10.6l-1.733-3h14.066l-1.733 3zm-7.333 11c1.1046 0 2-.8954 2-2s-.8954-2-2-2-2 .8954-2 2 .8954 2 2 2zm6 0c1.1046 0 2-.8954 2-2s-.8954-2-2-2-2 .8954-2 2 .8954 2 2 2zm-13.333-8l.933 4h11.8l2.133-4h-14.866z" />
                    </svg>
                    <span>{cart.length}</span>
                </div>
            </header>
            <div className="listProduct">
                {products.map(product => (
                    <div key={product.id} className="item">
                        <img src={product.image} alt={product.name} />
                        <h2>{product.name}</h2>
                        <p className="price">${product.price}</p>
                        <button onClick={() => addToCart(product)}>Add to Cart</button>
                    </div>
                ))}
            </div>
            <div className={`cartTab ${showCart ? 'show' : ''}`}>
                <h1>Cart</h1>
                <div className="listCart">
                    {cart.map((item, index) => (
                        <div key={index} className="item">
                            <img src={item.image} alt={item.name} />
                            <h2>{item.name}</h2>
                            <p className="price">${item.price}</p>
                        </div>
                    ))}
                </div>
                <div className="btn">
                    <button>Checkout</button>
                    <button className="close" onClick={toggleCart}>Close</button>
                </div>
            </div>
        </div>
    );
};

export default ShopPage;
