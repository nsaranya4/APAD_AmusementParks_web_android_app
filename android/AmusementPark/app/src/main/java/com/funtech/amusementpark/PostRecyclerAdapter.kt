package com.funtech.amusementpark

import android.content.Context
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.funtech.amusementpark.models.Post
import com.google.firebase.storage.FirebaseStorage
import com.google.firebase.storage.StorageReference
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.post_item.view.*

class PostRecyclerAdapter(private val posts: ArrayList<Post>, private val context: Context):
    RecyclerView.Adapter<PostRecyclerAdapter.PostHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PostRecyclerAdapter.PostHolder {
        val inflatedView = LayoutInflater.from(context).inflate(R.layout.post_item, parent, false)
        return PostRecyclerAdapter.PostHolder(inflatedView)
    }

    override fun getItemCount(): Int = posts.size

    override fun onBindViewHolder(holder: PostRecyclerAdapter.PostHolder, position: Int) {
        val post = posts[position]
        holder.bindPost(post)
    }

    class PostHolder(private val view: View) : RecyclerView.ViewHolder(view), View.OnClickListener {
        private var post: Post? = null

        init {
            view.setOnClickListener(this)
        }

        fun bindPost(post: Post) {
            this.post = post
            val storageRef = FirebaseStorage.getInstance().getReference()
            var imagesRef: StorageReference = storageRef.child(post.image_id)
            imagesRef.downloadUrl.addOnSuccessListener { uri ->
                Log.d("RecyclerView", uri.toString())
                Picasso.with(view.context).load(uri).into(view.post_image)
            }.addOnFailureListener {
                Log.e("RecyclerView", "Failed to download image")
            }
            view.post_title.text = post.title
            view.post_description.text = post.description
        }

        override fun onClick(v: View) {
            Log.d("RecyclerView", "CLICK!")
        }

        companion object {
            private val POST_KEY = "POST"
        }
    }

}