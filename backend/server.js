require('dotenv').config();
const express = require('express');
const path = require('path');
const leadsRouter = require('./routes/leads');
const pipelineRouter = require('./routes/pipeline');
const contentRouter = require('./routes/content');
const videosRouter = require('./routes/videos');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

// Static dashboard serving
app.use(express.static(path.join(__dirname, '../dashboard')));

// CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Routes
app.use('/api/leads', leadsRouter);
app.use('/api/pipeline', pipelineRouter);
app.use('/api/content', contentRouter);
app.use('/api/videos', videosRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`PluggedIN Backend running on port ${PORT}`);
});
