import React from 'react';
import {Link} from 'react-router-dom';

function ToolCard(props) {
  return (
    <div className="card">
      <Link to={props.cardData.url} className="card-body tool-card">
        <h4 className="card-title">{props.cardData.title}</h4>
        <h6 className="card-subtitle mb-2 text-muted">{props.cardData.description}</h6>
      </Link>
    </div>
  );
}

export default ToolCard;
