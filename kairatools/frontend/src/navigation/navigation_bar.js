import React from 'react';
import { Link } from 'react-router-dom';

function NavigationBar() {
  return (
    <div>
      <nav className="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
        <Link className="navbar-brand" to="/">Kairatools</Link>
      </nav>
    </div>
  )
}

export default NavigationBar;
