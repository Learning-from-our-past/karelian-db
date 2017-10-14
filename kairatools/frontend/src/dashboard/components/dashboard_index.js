import React, { Component } from 'react';
import { connect } from 'react-redux';

class DashboardIndex extends Component {
  render() {
    return (
      <div>
        <h2>Content will be here</h2>
        <p>Something tremendouss</p>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {};
}

export default connect(mapStateToProps)(DashboardIndex);
