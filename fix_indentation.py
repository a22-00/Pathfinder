import os
import re

def fix_job_seeker_file():
    """Fix the structural errors in job_seeker.py"""
    file_path = "project_learn_track/job_seeker.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    old_chat_pattern = r"(# Generate recommendations if appropriate\s+recommendations = \[\]\s+topic = get_topic_from_message\(user_message\)\s+if any\(word in user_message\.lower\(\) for word in \['help', 'recommend', 'suggest', 'advice'\]\):\s+recommendations = \[\s+f\"Take a \{topic\} skills assessment\",\s+f\"Explore \{topic\} job market trends\",\s+f\"Update your \{topic\} skills\",\s+f\"Connect with \{topic\} professionals\"\s+\]\s+)\s+return jsonify\(\{\s+'response': ai_response,\s+'conversation_id': conversation\.id,\s+'recommendations': recommendations\s+\}\)\s+except Exception as e:"
    
    new_chat_block = """        # Generate recommendations if appropriate
        recommendations = []
        topic = get_topic_from_message(user_message)
        if any(word in user_message.lower() for word in ['help', 'recommend', 'suggest', 'advice']):
            recommendations = [
                f"Take a {topic} skills assessment",
                f"Explore {topic} job market trends",
                f"Update your {topic} skills",
                f"Connect with {topic} professionals"
            ]
        
        return jsonify({
            'response': ai_response,
            'conversation_id': conversation.id,
            'recommendations': recommendations
        })
        
    except Exception as e:"""
    
    old_assessment_pattern = r"(# Log activity\s+log_user_activity\(current_user\.id, 'assessment_start', f'Started \{topic\} assessment'\)\s+)\s+return jsonify\(\{\s+'session_id': session_id,\s+'total_questions': len\(questions\),\s+'first_question': questions\[0\] if questions else None\s+\}\)\s+except Exception as e:"
    
    new_assessment_block = """        # Log activity
        log_user_activity(current_user.id, 'assessment_start', f'Started {topic} assessment')
        
        return jsonify({
            'session_id': session_id,
            'total_questions': len(questions),
            'first_question': questions[0] if questions else None
        })
        
    except Exception as e:"""
    
    fixed_content = content
    
    if "return jsonify({\n        'response': ai_response,\n            'conversation_id': conversation.id," in content:
        fixed_content = fixed_content.replace(
            "return jsonify({\n        'response': ai_response,\n            'conversation_id': conversation.id,\n            'recommendations': recommendations\n    })\n        \n    except Exception as e:",
            "        return jsonify({\n            'response': ai_response,\n            'conversation_id': conversation.id,\n            'recommendations': recommendations\n        })\n        \n    except Exception as e:"
        )
    
    if "return jsonify({\n            'session_id': session_id,\n            'total_questions': len(questions)," in content:
        fixed_content = fixed_content.replace(
            "return jsonify({\n            'session_id': session_id,\n            'total_questions': len(questions),\n            'first_question': questions[0] if questions else None\n        })\n        \n    except Exception as e:",
            "        return jsonify({\n            'session_id': session_id,\n            'total_questions': len(questions),\n            'first_question': questions[0] if questions else None\n        })\n        \n    except Exception as e:"
        )
    
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed structural errors in job_seeker.py")

if __name__ == "__main__":
    fix_job_seeker_file() 