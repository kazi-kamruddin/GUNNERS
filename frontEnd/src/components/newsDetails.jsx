import React from "react";
import '../allCss/newsDetails.css'

const NewsDetails = ({ news }) => {
  return (
    <div className="whole">
      <div className="title">
        <h2>{news.title}</h2>
      </div>
      <div className="body">
        <img src={news.imageLink} alt="News" className="image" />
        <p>{news.body}</p>
      </div>
      <div className="footer">
        <p className="date">{new Date(news.createdAt).toLocaleDateString()}</p>
      </div>
    </div>
  );
};

export default NewsDetails;


// const NewsDetails = ({ news }) => {

//     return (
//       <div className="newsDetails">
//         <h4>{news.title}</h4>
//         <p>{news.body}</p>
//         <img src={news.imageLink} alt="didnt load"></img>
//         <p>{news.createdAt}</p>
//       </div>
//     )
//   }
  
//   export default NewsDetails;