import './dashboard_index.css';
import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'lodash';
import ToolCard from './tool_card';

class DashboardIndex extends Component {
  renderCards() {
    return _.map(this.props.dashboard.availableTools, card => {
      return (
        <ToolCard key={card.key} cardData={card}/>
      );
    });
  }

  render() {
    return (
      <div className="row">
        <div className="col-8">
          <h1 className="dashboard-header">Tools</h1>

          <div className="row">
            <div className="col-12">
              {this.renderCards()}
            </div>
          </div>
        </div>
        <div className="col-4">
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return { dashboard: state.dashboard};
}

export default connect(mapStateToProps)(DashboardIndex);
