const NewsDetails = ({ news }) => {

    return (
      <div className="newsDetails">
        <h4>{news.title}</h4>
        <p>{news.body}</p>
        <img src={news.imageLink} alt="didnt load"></img>
        <p>{news.createdAt}</p>
      </div>
    )
  }
  
  export default NewsDetails;