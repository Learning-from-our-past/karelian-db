import { combineReducers } from 'redux';
import { reducer as formReducer } from 'redux-form';
import DashboardReducer from './reducer_dashboard';

const rootReducer = combineReducers({
  form: formReducer,
  dashboard: DashboardReducer
});

export default rootReducer;
