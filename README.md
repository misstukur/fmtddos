# FAIZA-DDOS
# DDoS Early Detection System (ML)

A machine learning-based system designed to detect Distributed Denial of Service (DDoS) attacks in their early stages by analyzing network traffic patterns. This project utilizes real-time data streams and anomaly detection algorithms to minimize false positives and reduce latency in threat response.

## 🚀 Overview

Traditional firewall and signature-based detection often struggle with zero-day DDoS attacks or low-and-slow attacks. This model focuses on **early detection** using behavioral analysis of network packets. By training on features like packet size distribution, inter-arrival times, and protocol flags, the system identifies anomalies before the network saturation point is reached.

## ✨ Key Features

- **Real-time Analysis**: Processes network flow data (NetFlow/IPFIX) for immediate threat assessment.
- **Multi-Algorithm Support**: Implements and compares Random Forest, LSTM, and HYBRID RF-LSTM models.
- **Low False Positive Rate**: Optimized for production environments to avoid blocking legitimate traffic.
- **Early Warning System**: Detects attack signatures in the reconnaissance or low-volume phase.
- **Visualization Dashboard**: Integrated metrics for traffic anomaly visualization.

## 📊 Dataset

This project is trained and tested using the following public datasets (configurable):
- **Bccc-cpacket-cloud-ddos-2024-dataset**: Contains realistic DDoS attack scenarios.
- **Custom Traffic Logs**: (Optional) User-provided PCAP files converted to flow data.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.9+ |
| **ML Frameworks** | Scikit-learn, TensorFlow/Keras, PyTorch |
| **Data Processing** | Pandas, NumPy, Scapy, CICFlowMeter |
| **Visualization** | Matplotlib, Seaborn, Plotly |
| **Deployment** | Streamlit |


