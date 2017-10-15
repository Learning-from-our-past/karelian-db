import './dashboard_index.css';
import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

class DashboardIndex extends Component {
  render() {
    return (
      <div className="row">
        <div className="col-8">
          <h1 className="dashboard-header">Dashboard</h1>

          {/*TODO: These cards should likely be components and generated from some data structure based on user rights*/}
          <div className="row">
            <div className="col-6">
              <div className="card">
                <Link to="/download" className="card-body tool-card">
                  <h4 className="card-title">Download data</h4>
                  <h6 className="card-subtitle mb-2 text-muted">Download data in CSV format</h6>
                </Link>
              </div>
            </div>
            <div className="col-6">
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
  return {};
}

export default connect(mapStateToProps)(DashboardIndex);
