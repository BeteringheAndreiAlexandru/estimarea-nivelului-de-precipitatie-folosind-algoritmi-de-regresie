#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <numeric>
#include <cmath>
#include <random>
#include <algorithm>
#include <iostream>

namespace py = pybind11;
using namespace std;


struct Node {
    bool is_leaf;
    double value;           
    int feature_index;      
    double threshold;       
    Node* left;
    Node* right;

    Node() : is_leaf(false), value(0.0), feature_index(-1), threshold(0.0), left(nullptr), right(nullptr) {}
    ~Node() { 
        delete left; 
        delete right; 
    }
};


class DecisionTree {
private:
    int max_depth;
    Node* root;

    double calculate_mean(const vector<double>& y, const vector<int>& indices) {
        if (indices.empty()) return 0.0;
        double sum = 0;
        for (int idx : indices) sum += y[idx];
        return sum / indices.size();
    }

    
    Node* build_tree(const vector<vector<double>>& X, const vector<double>& y, vector<int> indices, int depth, vector<double>& importances) {
        Node* node = new Node();

        if (depth >= max_depth || indices.size() <= 2) {
            node->is_leaf = true;
            node->value = calculate_mean(y, indices);
            return node;
        }

        int best_feature = -1;
        double best_threshold = 0.0;
        double best_variance_reduction = -1.0;

        int num_features = X[0].size();
        for (int f = 0; f < num_features; ++f) {
            for (size_t i = 0; i < min(indices.size(), (size_t)10); ++i) {
                double thresh = X[indices[i]][f];
                
                vector<int> left_idx, right_idx;
                for (int idx : indices) {
                    if (X[idx][f] <= thresh) left_idx.push_back(idx);
                    else right_idx.push_back(idx);
                }

                if (left_idx.empty() || right_idx.empty()) continue;

                double mean_left = calculate_mean(y, left_idx);
                double mean_right = calculate_mean(y, right_idx);
                
                // Calculul "Variance Reduction" (Simplificat ca diferenta absoluta)
                double diff = abs(mean_left - mean_right);

                if (diff > best_variance_reduction) {
                    best_variance_reduction = diff;
                    best_feature = f;
                    best_threshold = thresh;
                }
            }
        }

        if (best_feature == -1) {
            node->is_leaf = true;
            node->value = calculate_mean(y, indices);
            return node;
        }

       
        importances[best_feature] += best_variance_reduction * indices.size();

        vector<int> left_indices, right_indices;
        for (int idx : indices) {
            if (X[idx][best_feature] <= best_threshold) left_indices.push_back(idx);
            else right_indices.push_back(idx);
        }

        node->feature_index = best_feature;s
        node->threshold = best_threshold;
        node->left = build_tree(X, y, left_indices, depth + 1, importances);
        node->right = build_tree(X, y, right_indices, depth + 1, importances);

        return node;
    }

    double predict_single(Node* node, const vector<double>& row) {
        if (node->is_leaf) return node->value;
        if (row[node->feature_index] <= node->threshold) return predict_single(node->left, row);
        else return predict_single(node->right, row);
    }

public:
    DecisionTree(int max_depth) : max_depth(max_depth), root(nullptr) {}
    ~DecisionTree() { delete root; }

    void fit(const vector<vector<double>>& X, const vector<double>& y, const vector<int>& indices, vector<double>& importances) {
        root = build_tree(X, y, indices, 0, importances);
    }

    double predict(const vector<double>& row) {
        return predict_single(root, row);
    }
};

// Clasa principală: Pădurea Aleatoare (Random Forest)
class CustomRandomForest {
private:
    int n_estimators;
    int max_depth;
    vector<DecisionTree*> trees;
    vector<double> feature_importances; 

public:
    CustomRandomForest(int n_estimators = 10, int max_depth = 5) 
        : n_estimators(n_estimators), max_depth(max_depth) {}

    ~CustomRandomForest() {
        for (auto tree : trees) delete tree;
    }

    void fit(const vector<vector<double>>& X, const vector<double>& y) {
        random_device rd;
        mt19937 gen(rd());

        // Inițializăm scorurile cu 0 pentru fiecare coloană de date
        int num_features = X[0].size();
        feature_importances.assign(num_features, 0.0);

        for (int i = 0; i < n_estimators; ++i) {
            DecisionTree* tree = new DecisionTree(max_depth);
            
            vector<int> subset_indices;
            uniform_int_distribution<> dist(0, X.size() - 1);
            for (size_t j = 0; j < X.size(); ++j) {
                subset_indices.push_back(dist(gen));
            }

            tree->fit(X, y, subset_indices, feature_importances);
            trees.push_back(tree);
        }

        // 🌟 NOU: Normalizăm importanțele pentru a suma la 100%
        double total_importance = 0.0;
        for (double imp : feature_importances) total_importance += imp;
        
        if (total_importance > 0) {
            for (double& imp : feature_importances) {
                imp = (imp / total_importance) * 100.0;
            }
        }
        
        cout << "[C++] Custom Random Forest antrenat. XAI calculat cu succes!" << endl;
    }

    vector<double> predict(const vector<vector<double>>& X) {
        vector<double> predictions;
        for (const auto& row : X) {
            double sum = 0.0;
            for (auto tree : trees) sum += tree->predict(row);
            predictions.push_back(sum / trees.size()); 
        }
        return predictions;
    }

    
    vector<double> get_feature_importances() {
        return feature_importances;
    }
};

// ---------------------------------------------------------
// PYBIND11
// ---------------------------------------------------------
PYBIND11_MODULE(custom_rf, m) {
    m.doc() = "Modul Random Forest cu suport XAI nativ scris in C++";

    py::class_<CustomRandomForest>(m, "CustomRandomForest")
        .def(py::init<int, int>(), py::arg("n_estimators") = 10, py::arg("max_depth") = 5)
        .def("fit", &CustomRandomForest::fit)
        .def("predict", &CustomRandomForest::predict)
        .def("get_feature_importances", &CustomRandomForest::get_feature_importances); // 🌟 Funcția nouă adăugată în punte
}